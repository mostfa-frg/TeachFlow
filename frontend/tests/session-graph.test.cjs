const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const read=file=>fs.readFileSync(path.join(__dirname,'..',file),'utf8');
const context=vm.createContext({});
vm.runInContext(read('js/graph.js'),context);

test('hydrating and saving a draft preserves explicit empty links and secondary topics',()=>{
  const topics=['a','b'].map(id=>({id:'internal-'+id,stable_id:id,title:id,description:id,learning_objectives:[id]}));
  const version={topics,sessions:[{stable_id:'one',id:'internal-one',topic_id:'internal-a',topic_ids:['a','b'],
    title:'One',description:'Read',learning_objectives:['Read'],duration_minutes:40,sequence_index:1}],
    session_edges:[],dependencies:[]};
  const saved=context.proposalForSave({...context.graphFromVersion(version),roadmapProposal:version});
  assert.deepEqual(Array.from(saved.sessions[0].topic_ids),['a','b']);
  assert.equal(saved.session_edges.length,0);
  assert.equal(saved.topics.length,2);
});

test('legacy session identifiers are escaped in rendered attributes',()=>{
  const script=read('index.html').match(/<script>([\s\S]*?)<\/script>/)[1];
  const line=name=>script.split('\n').find(row=>row.startsWith('function '+name+'('));
  const id='lesson&one';
  const ctx=vm.createContext({state:{},positionsFor:()=>({positions:{[id]:{x:1,y:1}},width:200,height:200}),roadmapSvg:()=>''});
  vm.runInContext(line('escape')+'\n'+line('roadmapCanvas'),ctx);
  const html=ctx.roadmapCanvas([{id,title:'Saved session',minutes:20}],[],null,null,true);
  assert.ok(html.includes('data-id="lesson&amp;one"'));
});
