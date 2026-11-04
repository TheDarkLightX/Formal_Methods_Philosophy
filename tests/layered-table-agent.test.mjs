import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {loadKnowledge} from '../labs/layered-table-agent/assets.mjs';
import {encode,createEvaluator} from '../labs/layered-table-agent/runtime.mjs';

const root=new URL('../labs/layered-table-agent/',import.meta.url);
const read=name=>readFileSync(new URL(name,root));
const model=JSON.parse(read('model.json'));

test('published assets retain the frozen research identities',async()=>{
  const report=JSON.parse(read('report.json'));
  assert.equal(report.metadata.provisional,false);
  assert.ok(report.metadata.trainedTopicTables>=100000);
  assert.deepEqual(model.metadata,report.metadata);
  for(const [name,expected] of Object.entries(report.assets)){
    const bytes=read(name);
    assert.equal(bytes.length,expected.bytes);
    assert.equal(createHash('sha256').update(bytes).digest('hex'),expected.sha256);
  }
  const raw=gunzipSync(read('knowledge.json.gz'));
  assert.equal(raw.length,report.canonicalKnowledge.bytes);
  assert.equal(createHash('sha256').update(raw).digest('hex'),report.canonicalKnowledge.sha256);
  assert.deepEqual(await loadKnowledge(async name=>new Response(read(name)),false),JSON.parse(raw));
  assert.deepEqual(gunzipSync(read('model.json.gz')),read('model.json'));
  const knowledge=JSON.parse(raw);
  assert.equal(knowledge.records.length,report.retrieval_records);
  assert.ok(knowledge.records.every(r=>r.source.startsWith('https://huggingface.co/datasets/')&&['Apache-2.0','CC-BY-SA-3.0'].includes(r.license)));
});

test('the deployed Wasm preserves all Python fixture class votes',async()=>{
  const fixtures=JSON.parse(readFileSync(new URL('layered-table-parity.json',import.meta.url)));
  const evaluator=await createEvaluator(model.topic,read('evaluator.wasm'));
  assert.equal(evaluator.backend,'WebAssembly');
  for(const row of fixtures){
    const bits=encode(row.text,model.features);
    assert.deepEqual([...bits],row.bits);
    assert.deepEqual([...evaluator.evaluate(bits)],row.scores);
  }
});
