import {loadKnowledge} from './assets.mjs';
import {Agent} from './engine.mjs';
import {loadTau,TauGraph} from './tau-adapter.mjs';
import {evaluateJS} from './runtime.mjs';
let agent,tauGraph;
self.onmessage=async ({data})=>{try{
  if(data.type==='load') {const get=async name=>{const r=await fetch(new URL(name,import.meta.url));if(!r.ok)throw Error('Could not load '+name);return r;};
    const json=async name=>{if(typeof DecompressionStream==='function'){const r=await get(name+'.gz');return new Response(r.body.pipeThrough(new DecompressionStream('gzip'))).json();}return (await get(name)).json();};
    const [bundle,cards,knowledge,wasm]=await Promise.all([json('model.json'),(await get('cards.json')).json(),loadKnowledge(get),(await get('evaluator.wasm')).arrayBuffer()]);
    agent=await Agent.create(bundle,cards,knowledge,wasm);self.postMessage({type:'ready',metadata:bundle.metadata,backend:agent.topic.backend,records:knowledge.records.length});
  } else if(data.type==='tau-load') {
    if(!agent)throw Error('Load the model first.');
    const tau=await loadTau(data.module,data.wasm),g=agent.bundle.topic;
    const native=new TauGraph(g,tau,{onProgress:(done,total)=>self.postMessage({type:'tau-progress',done,total})});
    try {for(const value of [0,1]){const bits=new Uint8Array(g.inputs).fill(value),actual=native.evaluate(bits),expected=evaluateJS(g,bits);if(actual.some((x,i)=>x!==expected[i]))throw Error('Tau disagreed with the reference evaluator.');}}
    catch(error){native.free();throw error;}
    if(tauGraph)tauGraph.free();tauGraph=native;
    agent.topic={evaluate:x=>native.evaluate(x),backend:'Tau 0.8 gate tables'};
    self.postMessage({type:'tau-ready'});
  } else if(data.type==='clear'){if(agent)agent.context=null;}
  else if(data.type==='chat'){if(!agent)throw Error('The tables are still loading.');self.postMessage({type:'reply',id:data.id,result:agent.reply(data.text)});}
}catch(error){self.postMessage({type:'error',id:data.id,message:error.message});}};
