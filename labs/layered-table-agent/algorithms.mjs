// Independent, bounded algorithm implementations. No dynamic code evaluation.
export const commands = [
  'sort [9,2,7,2,1]', 'search 7 in [1,3,7,9,12]',
  'bfs A D: A-B, A-C, B-D, C-D',
  'dijkstra A D: A-B:4, A-C:1, C-B:2, B-D:1',
  'toposort: plan-build, build-test, test-release',
  'knapsack 7: 3:4, 4:5, 2:3', 'coins 6 with [1,3,4]',
  'edit kitten -> sitting', 'lcs ABCBDAB / BDCABA',
  'lis [10,9,2,5,3,7,101,18]', 'gcd 1071 462',
  'primes 100', 'powmod 7 128 13', 'fib 100'
];
const require = (p,m) => { if (!p) throw new Error(m); };
const integer = (s,lo=-1e9,hi=1e9) => { const n=Number(s); require(/^-?\d+$/.test(String(s).trim()) && Number.isSafeInteger(n) && n>=lo && n<=hi,`Use an integer from ${lo} to ${hi}.`); return n; };
const array = s => { let a; try { a=JSON.parse(s); } catch { throw new Error('Use a JSON array, such as [3,1,2].'); } require(Array.isArray(a)&&a.length<=256&&a.every(n=>Number.isSafeInteger(n)&&Math.abs(n)<=1e9),'Use at most 256 integers with absolute value at most one billion.'); return a; };
const result = (topic,title,value,steps,cost) => ({kind:'algorithm',topic,title,value,steps,cost});
export function normalizeCommand(text) {
  let m;
  if((m=/^(?:(?:can|could) you |please )?sort (?:these numbers:? )?(\[.*\])[?.!]*$/i.exec(text)))return 'sort '+m[1];
  if((m=/^(?:what is|what's|calculate|find) (?:the )?(?:gcd|greatest common divisor) (?:of )?(-?\d{1,50})\s*(?:and|,)\s*(-?\d{1,50})[?.!]*$/i.exec(text)))return 'gcd '+m[1]+' '+m[2];
  if((m=/^find (-?\d+) in (\[.*\])[?.!]*$/i.exec(text)))return 'search '+m[1]+' in '+m[2];
  return text;
}
function graph(text,weighted=false) {
  const edges=[], vertices=new Set();
  const parts=text.split(',').map(s=>s.trim());require(parts.length<=128,'Use at most 128 edges.');
  for(const p of parts){
    const m=/^([A-Za-z][A-Za-z0-9_]{0,15})(->|-)([A-Za-z][A-Za-z0-9_]{0,15})(?::(-?\d+))?$/.exec(p);
    require(m,'Edges look like A-B, A->B, or A-B:4.');
    require(!weighted||m[4]!==undefined,'Weighted edges need a weight, such as A-B:4.');
    const w=m[4]===undefined?1:integer(m[4],0,1e6);
    require(weighted||m[4]===undefined,'Omit weights for this unweighted command.');
    edges.push([m[1],m[3],w,m[2]==='->']);vertices.add(m[1]);vertices.add(m[3]);
  }
  require(vertices.size<=64,'Use at most 64 vertices.');return {edges,vertices:[...vertices]};
}
export function execute(text) {
  require(typeof text==='string'&&text.length<=2000,'Use at most 2,000 characters.');
  let m;const t=normalizeCommand(text.trim());
  if((m=/^sort\s+(\[.*\])$/i.exec(t))){
    const input=array(m[1]),a=input.slice(),steps=[];
    for(let width=1;width<a.length;width*=2){
      for(let start=0;start<a.length;start+=2*width){
        const left=a.slice(start,start+width),right=a.slice(start+width,start+2*width);let i=0,j=0,k=start;
        while(i<left.length||j<right.length)a[k++]=(j===right.length||(i<left.length&&left[i]<=right[j]))?left[i++]:right[j++];
      }steps.push(`Merge runs of length ${width}: [${a.join(', ')}]`);
    }return result('merge_sort','Stable merge sort',a,steps,'O(n log n) time and O(n) working storage. Retaining the displayed merge trace adds O(n log n) output storage.');
  }
  if((m=/^search\s+(-?\d+)\s+in\s+(\[.*\])$/i.exec(t))){
    const target=integer(m[1]),a=array(m[2]);require(a.every((v,i)=>!i||a[i-1]<=v),'Binary search requires sorted input.');let lo=0,hi=a.length;const steps=[];
    while(lo<hi){const mid=lo+Math.floor((hi-lo)/2);steps.push(`[${lo}, ${hi}): index ${mid} contains ${a[mid]}`);if(a[mid]<target)lo=mid+1;else hi=mid;}
    return result('binary_search','Lower-bound binary search',lo<a.length&&a[lo]===target?{index:lo,value:target}:{found:false,insertionIndex:lo},steps,'The search uses O(log n) comparisons. This tool first checks that the supplied array is sorted, which takes O(n) time.');
  }
  if((m=/^(bfs|dijkstra)\s+(\w+)\s+(\w+):\s*(.+)$/i.exec(t))){
    const weighted=m[1].toLowerCase()==='dijkstra',start=m[2],end=m[3],g=graph(m[4],weighted);
    require(g.vertices.includes(start)&&g.vertices.includes(end),'Both endpoints must occur in the graph.');
    const adj=new Map(g.vertices.map(v=>[v,[]]));for(const [a,b,w,directed] of g.edges){adj.get(a).push([b,w]);if(!directed)adj.get(b).push([a,w]);}
    const dist=new Map(g.vertices.map(v=>[v,Infinity])),prev=new Map(),done=new Set(),steps=[],queue=[start];let head=0;dist.set(start,0);
    while(weighted?done.size<g.vertices.length:head<queue.length){
      let u;
      if(weighted){for(const v of g.vertices)if(!done.has(v)&&(u===undefined||dist.get(v)<dist.get(u)))u=v;if(!u||!Number.isFinite(dist.get(u)))break;}
      else u=queue[head++];
      done.add(u);steps.push(`Visit ${u}, distance ${dist.get(u)}`);if(u===end)break;
      for(const [v,w] of adj.get(u))if(!done.has(v)&&dist.get(u)+w<dist.get(v)){const fresh=dist.get(v)===Infinity;dist.set(v,dist.get(u)+w);prev.set(v,u);if(!weighted&&fresh)queue.push(v);}
    }
    const path=[];if(Number.isFinite(dist.get(end))){for(let v=end;v!==undefined;v=prev.get(v))path.push(v);path.reverse();}
    return result(weighted?'dijkstra':'bfs',weighted?'Dijkstra (bounded array frontier)':'Breadth-first search',{path,distance:Number.isFinite(dist.get(end))?dist.get(end):null},steps,weighted?'This tool scans the remaining vertices: O(V² + E) time and O(V + E) storage, plus the displayed trace.':'The queue uses a moving head index: O(V + E) time and O(V + E) storage, plus the displayed trace.');
  }
  if((m=/^toposort:\s*(.+)$/i.exec(t))){
    const g=graph(m[1]),indeg=new Map(g.vertices.map(v=>[v,0])),adj=new Map(g.vertices.map(v=>[v,[]]));
    for(const [a,b] of g.edges){adj.get(a).push(b);indeg.set(b,indeg.get(b)+1);}
    const queue=g.vertices.filter(v=>indeg.get(v)===0),order=[],steps=[];let head=0;
    while(head<queue.length){const v=queue[head++];order.push(v);steps.push(`Remove ${v} (indegree zero)`);for(const b of adj.get(v)){indeg.set(b,indeg.get(b)-1);if(indeg.get(b)===0)queue.push(b);}}
    return result('topological','Topological ordering',order.length===g.vertices.length?{order}:{cycle:true,orderedPrefix:order},steps,'O(V + E) time and O(V + E) storage. Ready vertices follow deterministic input order.');
  }
  if((m=/^knapsack\s+(\d+):\s*(.+)$/i.exec(t))){
    const capacity=integer(m[1],0,2000),parts=m[2].split(',');require(parts.length<=64,'Use at most 64 items.');
    const items=parts.map((part,i)=>{const x=/^\s*(\d+):(\d+)\s*$/.exec(part);require(x,'Items look like weight:value.');return {weight:integer(x[1],1,2000),value:integer(x[2],0,1e6),index:i};});
    let dp=Array.from({length:capacity+1},()=>({value:0,items:[]}));const steps=[];
    for(const item of items){for(let c=capacity;c>=item.weight;c--){const prev=dp[c-item.weight];if(prev.value+item.value>dp[c].value)dp[c]={value:prev.value+item.value,items:[...prev.items,item.index]};}steps.push(`After item ${item.index} (${item.weight}:${item.value}), best value = ${dp[capacity].value}`);}
    return result('knapsack','Zero-one knapsack',dp[capacity],steps,'This version copies selected-item lists: O(n²W) worst-case time and O(nW) stored item indices. A value-only implementation needs O(nW) time and O(W) memory.');
  }
  if((m=/^coins\s+(\d+)\s+with\s+(\[.*\])$/i.exec(t))){
    const amount=integer(m[1],0,5000),coins=[...new Set(array(m[2]))].sort((a,b)=>a-b);require(coins.length<=32&&coins.every(c=>c>0),'Use up to 32 positive denominations.');
    const dp=Array(amount+1).fill(Infinity),last=Array(amount+1).fill(null);dp[0]=0;
    for(let a=1;a<=amount;a++)for(const c of coins)if(c<=a&&dp[a-c]+1<dp[a]){dp[a]=dp[a-c]+1;last[a]=c;}
    const chosen=[];if(Number.isFinite(dp[amount]))for(let a=amount;a>0;a-=last[a])chosen.push(last[a]);
    return result('coin_change','Minimum coin count',Number.isFinite(dp[amount])?{count:dp[amount],coins:chosen}:{reachable:false},dp.slice(0,Math.min(amount+1,25)).map((v,a)=>`Amount ${a}: ${Number.isFinite(v)?v:'unreachable'}`));
  }
  if((m=/^edit\s+(.*?)\s*->\s*(.*?)$/i.exec(t))){
    const a=[...m[1]],b=[...m[2]];require(a.length<=128&&b.length<=128,'Use strings of at most 128 Unicode code points.');
    const dp=Array.from({length:a.length+1},(_,i)=>Array.from({length:b.length+1},(_,j)=>!i?j:!j?i:0));
    for(let i=1;i<=a.length;i++)for(let j=1;j<=b.length;j++)dp[i][j]=Math.min(dp[i-1][j]+1,dp[i][j-1]+1,dp[i-1][j-1]+Number(a[i-1]!==b[j-1]));
    return result('edit_distance','Levenshtein distance',{distance:dp[a.length][b.length]},dp.slice(0,20).map((row,i)=>`Prefix length ${i}: ${row.slice(0,25).join(' ')}`),'O(mn) time. This tool keeps the full O(mn) table to display prefix states.');
  }
  if((m=/^lcs\s+(.*?)\s*\/\s*(.*?)$/i.exec(t))){
    const a=[...m[1]],b=[...m[2]];require(a.length<=128&&b.length<=128,'Use strings of at most 128 Unicode code points.');const dp=Array.from({length:a.length+1},()=>Array(b.length+1).fill(0));
    for(let i=1;i<=a.length;i++)for(let j=1;j<=b.length;j++)dp[i][j]=a[i-1]===b[j-1]?dp[i-1][j-1]+1:Math.max(dp[i-1][j],dp[i][j-1]);
    let i=a.length,j=b.length,out=[];while(i&&j){if(a[i-1]===b[j-1]){out.push(a[--i]);j--;}else if(dp[i-1][j]>=dp[i][j-1])i--;else j--;}
    return result('lcs','Longest common subsequence',{length:out.length,subsequence:out.reverse().join('')},[`Solved ${(a.length+1)*(b.length+1)} prefix states.`,`One optimal subsequence is shown; it need not be unique.`]);
  }
  if((m=/^lis\s+(\[.*\])$/i.exec(t))){
    const a=array(m[1]),tails=[],idx=[],prev=Array(a.length).fill(-1),steps=[];
    a.forEach((v,i)=>{let lo=0,hi=tails.length;while(lo<hi){const mid=(lo+hi)>>1;if(tails[mid]<v)lo=mid+1;else hi=mid;}if(lo)prev[i]=idx[lo-1];tails[lo]=v;idx[lo]=i;steps.push(`Read ${v}; smallest tails: [${tails.join(', ')}]`);});
    const seq=[];for(let i=idx.length?idx.at(-1):-1;i>=0;i=prev[i])seq.push(a[i]);
    return result('lis','Strictly increasing subsequence',{length:tails.length,sequence:seq.reverse()},steps,'The subsequence algorithm uses O(n log n) time and O(n) working storage. Materializing every displayed tails array can add O(n²) time and output storage.');
  }
  if((m=/^gcd\s+(-?\d{1,50})\s+(-?\d{1,50})$/i.exec(t))){
    let a=BigInt(m[1]),b=BigInt(m[2]);a=a<0n?-a:a;b=b<0n?-b:b;const steps=[];
    while(b){const r=a%b;steps.push(`${a} = ${a/b} × ${b} + ${r}`);[a,b]=[b,r];}
    return result('gcd','Euclidean algorithm',a.toString(),steps);
  }
  if((m=/^primes\s+(\d+)$/i.exec(t))){
    const n=integer(m[1],0,100000),s=new Uint8Array(n+1);s.fill(1,2);const steps=[];
    for(let p=2;p*p<=n;p++)if(s[p]){for(let k=p*p;k<=n;k+=p)s[k]=0;steps.push(`Mark multiples of ${p}, starting at ${p*p}`);}
    const primes=[];for(let p=2;p<=n;p++)if(s[p])primes.push(p);
    return result('primes','Sieve of Eratosthenes',{count:primes.length,primes:primes.slice(0,200),truncated:primes.length>200},steps);
  }
  if((m=/^powmod\s+(-?\d{1,50})\s+(\d{1,20})\s+(\d{1,50})$/i.exec(t))){
    const mod=BigInt(m[3]);require(mod>0n,'The modulus must be positive.');let base=((BigInt(m[1])%mod)+mod)%mod,e=BigInt(m[2]),value=1n%mod;const steps=[];
    while(e){if(e&1n)value=value*base%mod;steps.push(`Exponent ${e}, accumulator ${value}, base ${base}`);base=base*base%mod;e>>=1n;}
    return result('modular','Modular exponentiation',value.toString(),steps);
  }
  if((m=/^fib\s+(\d+)$/i.exec(t))){const n=integer(m[1],0,10000);let a=0n,b=1n;for(let i=0;i<n;i++)[a,b]=[b,a+b];return result('dynamic_programming','Fibonacci (exact integers)',a.toString(),[`F(0)=0, F(1)=1; ${n} recurrence steps.`,`Only the previous two values are retained.`]);}
  if(/^(sort|search|bfs|dijkstra|toposort:|knapsack|coins|edit|lcs|lis|gcd|primes|powmod|fib)(\s|$)/i.test(t))throw new Error('The command format was not recognized. Choose an example from Help.');
  return null;
}
