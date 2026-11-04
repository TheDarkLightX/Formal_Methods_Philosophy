// Adapter to the user's own Tau 0.8 ES-module/wasm pair. No Tau code is bundled.
import {validateGraph} from './runtime.mjs';
export function gateTerm(f,a,b) {
  const terms=[];for(let x=0;x<2;x++)for(let y=0;y<2;y++)if((f>>(3-2*x-y))&1)terms.push(`(${a}${x?'':"'"} & ${b}${y?'':"'"})`);
  return terms.length===0?'0':terms.length===4?'1':terms.join(' | ');
}
export function chunkSpec(graph,start,count=16) {
  const end=Math.min(start+count,graph.nodes.length),base=graph.inputs+start,external=new Set();
  for(let j=start;j<end;j++)for(const v of graph.nodes[j].slice(0,2))if(v<base)external.add(v);
  const inputs=[...external].sort((a,b)=>a-b),names=new Map(inputs.map((v,i)=>[v,'i'+i]));
  for(let j=start;j<end;j++)names.set(graph.inputs+j,'o'+(j-start));
  const ref=v=>names.get(v)+'[t]:sbf';
  const equations=graph.nodes.slice(start,end).map(([a,b,f],k)=>`o${k}[t]:sbf = (${gateTerm(f,`(${ref(a)})`,`(${ref(b)})`)})`);
  return {spec:'always (\n'+equations.join(' &&\n')+'\n).',inputs,start,count:end-start};
}
export const gateBankSpec = 'always (\n'+Array.from({length:16},(_,f)=>`o${f}[t]:sbf = (${gateTerm(f,'(i0[t]:sbf)','(i1[t]:sbf)')})`).join(' &&\n')+'\n).';
export class TauGraph {
  constructor(graph,tau,{onProgress=()=>{}}={}) {
    validateGraph(graph);this.graph=graph;this.tau=tau;this.handle=tau.interpreter_create(gateBankSpec);
    if(!this.handle)throw Error(tau.get_last_error()||'Tau refused the gate bank');onProgress(16,16);
  }
  evaluate(input) {
    const g=this.graph;if(input.length!==g.inputs||input.some(x=>x!==0&&x!==1))throw Error('Boolean input width mismatch');
    // All graph nodes share just 16 gate functions and four Boolean inputs.
    // Tau evaluates those 64 distinct applications. Exact memoization then
    // reuses their answers across the DAG; JS accumulates integer class votes.
    const table=Array.from({length:16},()=>new Uint8Array(4));
    for(let a=0;a<2;a++)for(let b=0;b<2;b++) {const r=this.tau.interpreter_step(this.handle,{i0:String(a),i1:String(b)});if(!r)throw Error(this.tau.get_last_error()||'Tau step had no result');for(let f=0;f<16;f++){const v=String(r.outputs['o'+f]).trim();if(v!=='0'&&v!=='1')throw Error('Tau returned a non-bit table output');table[f][2*a+b]=Number(v);}}
    const bits=new Uint8Array(g.inputs+g.nodes.length);bits.set(input);
    g.nodes.forEach(([a,b,f],j)=>bits[g.inputs+j]=table[f][2*bits[a]+bits[b]]);
    return Int32Array.from(g.votes,(group,c)=>g.bias[c]+group.reduce((s,[v,p])=>s+(bits[v]^p),0));
  }
  free(){if(this.handle)this.tau.interpreter_free(this.handle);this.handle=0;}
}
export async function loadTau(moduleFile,wasmFile) {
  if(!moduleFile.name.endsWith('.mjs')||!wasmFile.name.endsWith('.wasm'))throw Error('Choose the matching tau.esm.mjs and tau.esm.wasm files.');
  if(moduleFile.size>32*1024*1024||wasmFile.size>256*1024*1024)throw Error('The supplied runtime exceeds this lab’s loading limit.');
  const url=URL.createObjectURL(new Blob([await moduleFile.text()],{type:'text/javascript'}));
  const wasmUrl=URL.createObjectURL(new Blob([await wasmFile.arrayBuffer()],{type:'application/wasm'}));
  try {const {default:init}=await import(url);if(typeof init!=='function')throw Error('The module has no Tau factory export.');const tau=await init({locateFile:name=>{if(!name.endsWith('.wasm'))throw Error('Unexpected runtime asset: '+name);return wasmUrl;},print:()=>{},printErr:()=>{}});
    for(const name of ['valid','interpreter_create','interpreter_step','interpreter_free','get_last_error','set_charvar'])if(typeof tau[name]!=='function')throw Error('Missing Tau binding: '+name);
    tau.set_charvar(false);if(tau.valid('x:sbf = x:sbf.')!==true)throw Error('Tau runtime self-check did not decide true');
    return tau;
  } finally {URL.revokeObjectURL(url);URL.revokeObjectURL(wasmUrl);}
}
