// Pure, deterministic feature extraction and integer table evaluation.
const STOP = new Set('a an the is are was be to of for in on and or with me my i you it its can could would should do does how what why when which tell about please explain show give example simple terms step by beginner briefly algorithm lab learning project help understand studying need key outline main useful practice makes pitfalls watch intuitive account through'.split(' '));
const REL_STOP = new Set('a an the is are was were be been to of for in on and or with me my i you it its can could would should do does how what why when which tell about please explain show give this that these those as at by from your have has will just than if then not into'.split(' '));
export function tokens(text) {
  const words = (text.toLowerCase().match(/[a-z0-9]+/g) || []).filter(w => !STOP.has(w));
  const f = new Set(words.map(w => 'w:' + w));
  for (let i=1;i<words.length;i++) f.add('b:'+words[i-1]+'_'+words[i]);
  for (let w of words) if(w.length>=3) {w='^'+w+'$';for(let i=0;i<w.length-2;i++)f.add('c:'+w.slice(i,i+3));}
  return f;
}
export function encode(text, features) { const f=tokens(text);return Uint8Array.from(features,x=>+f.has(x)); }
export function terms(text) {return (text.toLowerCase().match(/[a-z0-9]+/g)||[]).filter(w=>!REL_STOP.has(w)).map(w=>w.endsWith('s')&&w.length>4&&!w.endsWith('ss')?w.slice(0,-1):w);}
const intersection=(a,b)=>[...a].filter(x=>b.has(x)).length;
export function relation(query,record) {
  const q=terms(query),d=terms(record.q),a=terms(record.a),qs=new Set(q),ds=new Set(d),aas=new Set(a),inter=intersection(qs,ds);
  const big=w=>new Set(w.slice(1).map((x,i)=>w[i]+'\0'+x)),qb=big(q),db=big(d);
  const values=[Math.floor(8*inter/Math.max(1,qs.size)),Math.floor(8*inter/Math.max(1,ds.size)),Math.floor(8*intersection(qs,aas)/Math.max(1,qs.size)),Math.floor(8*intersection(qb,db)/Math.max(1,qb.size)),Math.min(inter,8),Math.floor(8*inter/Math.max(1,new Set([...qs,...ds]).size)),Math.floor(8*Math.min(q.length,d.length)/Math.max(1,q.length,d.length)),+(q.join('\0')===d.join('\0'))*8];
  return Uint8Array.from(values.flatMap(v=>Array.from({length:8},(_,i)=>+(v>=i+1))));
}
export function validateGraph(g) {
  const int=(v,a,b)=>Number.isSafeInteger(v)&&v>=a&&v<=b;
  if(!g || !int(g.inputs,1,65536)||!int(g.classes,1,1024)||!Array.isArray(g.nodes)||g.nodes.length>1000000||!Array.isArray(g.votes)||g.votes.length!==g.classes||!Array.isArray(g.bias)||g.bias.length!==g.classes)throw Error('Invalid model shape');
  g.nodes.forEach((n,i)=>{if(!Array.isArray(n)||n.length!==3||!int(n[0],0,g.inputs+i-1)||!int(n[1],0,g.inputs+i-1)||!int(n[2],0,15))throw Error('Invalid table');});
  let total=0;g.votes.forEach((group,c)=>{if(!Array.isArray(group)||!int(g.bias[c],0,1000000))throw Error('Invalid votes');total+=group.length;for(const v of group)if(!Array.isArray(v)||v.length!==2||!int(v[0],0,g.inputs+g.nodes.length-1)||!int(v[1],0,1))throw Error('Invalid vote');});
  if(total>1000000)throw Error('Model exceeds vote budget');return g;
}
export function evaluateJS(g,input) {
  if(input.length!==g.inputs||input.some(x=>x!==0&&x!==1))throw Error('Boolean input width mismatch');
  const bits=new Uint8Array(g.inputs+g.nodes.length);bits.set(input);
  g.nodes.forEach(([a,b,f],i)=>bits[g.inputs+i]=(f>>(3-2*bits[a]-bits[b]))&1);
  return Int32Array.from(g.votes,(v,c)=>g.bias[c]+v.reduce((s,[i,p])=>s+(bits[i]^p),0));
}
export function wasmEvaluator(g,instance) {
  validateGraph(g);const memory=instance.exports.memory;let at=Number(instance.exports.__heap_base.value);
  const allocate=n=>{at=(at+3)&~3;const p=at;at+=n;return p;};
  const bits=allocate(g.inputs+g.nodes.length),nodes=allocate(g.nodes.length*12),votesArray=g.votes.flatMap((group,c)=>group.flatMap(([v,p])=>[v,p,c])),votes=allocate(votesArray.length*4),bias=allocate(g.classes*4),scores=allocate(g.classes*4);
  if(at>64*1024*1024)throw Error('Model memory exceeds 64 MiB');if(at>memory.buffer.byteLength)memory.grow(Math.ceil((at-memory.buffer.byteLength)/65536));
  new Uint32Array(memory.buffer,nodes,g.nodes.length*3).set(g.nodes.flat());new Uint32Array(memory.buffer,votes,votesArray.length).set(votesArray);new Int32Array(memory.buffer,bias,g.classes).set(g.bias);
  return input=>{if(input.length!==g.inputs||input.some(x=>x!==0&&x!==1))throw Error('Boolean input width mismatch');new Uint8Array(memory.buffer,bits,g.inputs).set(input);const status=instance.exports.evaluate(bits,g.inputs,nodes,g.nodes.length,votes,votesArray.length/3,bias,scores,g.classes);if(status!==0)throw Error('WASM model validation '+status);return new Int32Array(memory.buffer,scores,g.classes).slice();};
}
export async function createEvaluator(g,wasmBytes) {
  validateGraph(g);
  if(wasmBytes) {try {const {instance}=await WebAssembly.instantiate(wasmBytes,{});return {evaluate:wasmEvaluator(g,instance),backend:'WebAssembly'};}catch(error){return {evaluate:x=>evaluateJS(g,x),backend:'JavaScript',fallback:error.message};}}
  return {evaluate:x=>evaluateJS(g,x),backend:'JavaScript'};
}
export class RetrievalIndex {
  constructor(records) {this.records=records;this.index=new Map();this.lengths=[];this.sets=[];let sum=0;
    records.forEach((r,i)=>{const ts=terms(r.q),counts=new Map();this.sets.push(new Set(ts));this.lengths.push(ts.length);sum+=ts.length;for(const t of ts)counts.set(t,(counts.get(t)||0)+1);for(const [t,n] of counts){if(!this.index.has(t))this.index.set(t,[]);this.index.get(t).push([i,n]);}});this.average=sum/Math.max(1,records.length);
  }
  search(query,limit=12) {const qs=new Set(terms(query)),scores=new Map(),N=this.records.length;
    for(const t of qs){const rows=this.index.get(t)||[],idf=Math.log(1+(N-rows.length+.5)/(rows.length+.5));for(const [i,tf] of rows){const norm=tf+1.2*(.25+.75*this.lengths[i]/this.average);scores.set(i,(scores.get(i)||0)+idf*tf*2.2/norm);}}
    return [...scores].map(([i,score])=>({i,score,shared:intersection(qs,this.sets[i]),coverage:intersection(qs,this.sets[i])/Math.max(1,qs.size)})).sort((a,b)=>b.score-a.score||a.i-b.i).slice(0,limit);
  }
}
