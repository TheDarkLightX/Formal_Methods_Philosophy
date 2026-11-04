import {encode,relation,terms,createEvaluator,RetrievalIndex} from './runtime.mjs';
import {execute,commands} from './algorithms.mjs';
export class Agent {
  constructor(bundle,cards,knowledge,topic,relevance) {Object.assign(this,{bundle,cards,knowledge,topic,relevance});this.byId=new Map(cards.map(c=>[c.id,c]));this.index=new RetrievalIndex(knowledge.records);this.context=null;}
  static async create(bundle,cards,knowledge,wasmBytes) {return new Agent(bundle,cards,knowledge,await createEvaluator(bundle.topic,wasmBytes),await createEvaluator(bundle.relevance,wasmBytes));}
  reply(raw) {
    const started=performance.now(),text=raw.trim();if(!text||text.length>2000)throw Error('Use between 1 and 2,000 characters.');
    let result;const end=r=>({...r,trace:{...(r.trace||{}),backend:r.trace?.candidates||r.trace?.topics?this.topic.backend:'JavaScript',milliseconds:Math.round((performance.now()-started)*100)/100}});
    const showRecord=record=>({kind:'retrieved',title:'A related '+(record.dataset||'OpenAssistant')+' answer',text:record.a,sourceQuestion:record.q,sourceContext:record.context,source:record.source||this.knowledge.source,license:record.license||'Apache-2.0',dataset:record.dataset||'OpenAssistant',recordId:record.id});
    if(this.context?.pending&&/^(yes|yes please|show it|that one)[.! ]*$/i.test(text)){const record=this.context.pending;this.context={record};return end({...showRecord(record),trace:{route:'user-confirmed source match'}});}
    if(this.context?.record&&/^(source|where is that from|citation)[?.! ]*$/i.test(text))return end({...showRecord(this.context.record),text:'This is the original attributed answer. Its source question and license are below.',trace:{route:'conversation source'}});
    try{result=execute(text);}catch(error){return end({kind:'input',title:'Check the command',text:error.message,trace:{route:'bounded algorithm input check'}});}
    if(result){this.context={topic:result.topic,cost:result.cost};return end({...result,text:result.steps.join('\n'),trace:{route:'exact algorithm',topic:result.topic}});}
    if(/^(help|commands|tools)[?.!]*$/i.test(text))return end({kind:'help',title:'Try a calculation',text:commands.join('\n'),trace:{route:'command reference'}});
    const comparison=/^(?:compare\s+)?(.+?)\s+(?:versus|vs\.?|compared (?:with|to)|and)\s+(.+?)[?.!]*$/i.exec(text);
    if(comparison&&(/^(compare|difference)/i.test(text)||/ versus | vs\.? /i.test(text))) {
      const choices=comparison.slice(1).map(part=>{const s=Array.from(this.topic.evaluate(encode(part,this.bundle.features))),i=s.indexOf(Math.max(...s)),rank=[...s].sort((a,b)=>b-a),card=this.byId.get(this.bundle.ids[i]),q=new Set(terms(part)),supported=new Set(terms([card?.title,...(card?.aliases||[])].join(' ')));return rank[0]-rank[1]>=this.bundle.thresholds.topicMargin&&[...q].some(w=>supported.has(w))?card:null;});
      if(choices.every(c=>c&&!['unknown','hello','thanks'].includes(c.id))&&choices[0].id!==choices[1].id) {this.context=null;return end({kind:'comparison',title:choices.map(c=>c.title).join(' and '),text:choices.map(c=>c.title+'\n'+c.body+'\n'+c.cost+'\nWatch for: '+c.mistake).join('\n\n'),trace:{route:'two learned topic decisions',topics:choices.map(c=>c.id)}});}
    }
    const follow=/^(and |what about |can you (give |show |explain )?(an? )?)?(example|complexity|cost|pitfall|mistake|more|explain more|why|how does it work)[?.! ]*$/i.exec(text);
    if(follow&&this.context?.topic&&this.byId.has(this.context.topic)) {const c=this.byId.get(this.context.topic),mode=follow[4]?.toLowerCase()||'more';return end({kind:'card',title:c.title,text:/complexity|cost/.test(text)?(this.context.cost||c.cost):/pitfall|mistake/.test(text)?c.mistake:/example/.test(text)?c.example:c.body+'\n\n'+c.example,topic:c.id,trace:{route:'conversation follow-up',topic:c.id}});}
    const x=encode(text,this.bundle.features),scores=Array.from(this.topic.evaluate(x)),rank=scores.map((score,i)=>({score,id:this.bundle.ids[i]})).sort((a,b)=>b.score-a.score||this.bundle.ids.indexOf(a.id)-this.bundle.ids.indexOf(b.id));
    const top=rank[0],card=this.byId.get(top.id),margin=top.score-rank[1].score,qterms=new Set(terms(text));
    const support=card?new Set(terms([card.title,...card.aliases,card.body].join(' '))):new Set();
    const overlap=[...qterms].filter(w=>support.has(w)).length;
    const trace={route:'learned topic tables',topic:top.id,margin,activeFeatures:x.reduce((s,b)=>s+b,0),candidates:rank.slice(0,3)};
    const matches=this.index.search(text).map(m=>{const record=this.knowledge.records[m.i],s=Array.from(this.relevance.evaluate(relation(text,record)));return {...m,record,votes:s,accepted:s[1]>s[0]&&m.coverage>=.5&&m.shared>=2};});
    const match=matches.filter(m=>m.accepted).sort((a,b)=>b.coverage-a.coverage||b.score-a.score||a.i-b.i)[0];
    const conversational=['hello','thanks','limitations'].includes(top.id);
    if(card&&top.id!=='unknown'&&((margin>=this.bundle.thresholds.topicMargin&&overlap>=Math.min(2,qterms.size))||conversational&&margin>=this.bundle.thresholds.topicMargin)) {
      this.context={topic:card.id};return end({kind:'card',title:card.title,topic:card.id,text:card.body+'\n\n'+(/complexity|runtime|running time|cost/.test(text.toLowerCase())?card.cost:/example/.test(text.toLowerCase())?card.example:''),trace});
    }
    if(match){
      const detailCoverage=match.shared/Math.max(1,this.index.sets[match.i].size);
      if(detailCoverage<.6){this.context={pending:match.record};return end({kind:'clarify',title:'Does this match the question?',text:'The closest source asks: “'+match.record.q+'”\n\nReply “yes” to read that answer, or add a little more detail.',trace:{...trace,route:'clarify an incomplete source match',coverage:match.coverage,relevanceVotes:match.votes}});}
      this.context={record:match.record};return end({...showRecord(match.record),trace:{...trace,route:'retrieval + learned relevance tables',coverage:match.coverage,relevanceVotes:match.votes,bm25:match.score}});
    }
    this.context=null;return end({kind:'abstain',title:'I do not have a close enough match',text:'Try a concrete algorithm question, or run a calculation such as “dijkstra A D: A-B:4, A-C:1, C-B:2, B-D:1”. This is a compact table and retrieval experiment; it cannot compose a reliable answer to every question.',suggestions:rank.slice(0,3).map(r=>this.byId.get(r.id)?.title).filter(Boolean),trace:{...trace,route:'abstain'}});
  }
}
