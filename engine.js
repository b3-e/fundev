// ===================== Pseudocode engine =====================
const KEYWORDS = new Set(['FUNCTION','ENDFUNCTION','PROCEDURE','ENDPROCEDURE','RETURN',
  'IF','THEN','ELSE','ELSEIF','ENDIF','WHILE','DO','ENDWHILE','REPEAT','UNTIL',
  'FOR','TO','STEP','ENDFOR','OUTPUT','PRINT','AND','OR','NOT','MOD','DIV','TRUE','FALSE']);

class PseudoError extends Error {}
class ReturnSignal { constructor(value){ this.value = value; } }

function tokenize(src){
  const tokens=[]; let i=0, line=1; const n=src.length;
  const isDigit=c=>c>='0'&&c<='9';
  const isAlpha=c=>/[A-Za-z_]/.test(c);
  const isAlnum=c=>/[A-Za-z0-9_]/.test(c);
  while(i<n){
    const c=src[i];
    if(c==='\n'){ tokens.push(['NEWLINE','\n',line]); line++; i++; continue; }
    if(c===' '||c==='\t'||c==='\r'){ i++; continue; }
    if(c==='/'&&src[i+1]==='/'){ while(i<n&&src[i]!=='\n') i++; continue; }
    if(c==='#'){ while(i<n&&src[i]!=='\n') i++; continue; }
    if(isDigit(c)){
      let j=i; while(j<n&&isDigit(src[j])) j++;
      let isFloat=false;
      if(src[j]==='.'&&isDigit(src[j+1])){ isFloat=true; j++; while(j<n&&isDigit(src[j])) j++; }
      const text=src.slice(i,j);
      tokens.push(['NUMBER', isFloat?parseFloat(text):parseInt(text,10), line]);
      i=j; continue;
    }
    if(c==='"'||c==="'"){
      const quote=c; let j=i+1; let buf='';
      while(j<n && src[j]!==quote){
        if(src[j]==='\\'){ buf+=src[j+1]; j+=2; } else { buf+=src[j]; j++; }
      }
      tokens.push(['STRING', buf, line]); i=j+1; continue;
    }
    const two=src.slice(i,i+2);
    if(['==','!=','<=','>=','<-'].includes(two)){ tokens.push([two,two,line]); i+=2; continue; }
    if('+-*/=<>'.includes(c)){ tokens.push([c,c,line]); i++; continue; }
    if(c==='['){ tokens.push(['LBRACKET','[',line]); i++; continue; }
    if(c===']'){ tokens.push(['RBRACKET',']',line]); i++; continue; }
    if(c==='{'){ tokens.push(['LBRACE','{',line]); i++; continue; }
    if(c==='}'){ tokens.push(['RBRACE','}',line]); i++; continue; }
    if(c==='('){ tokens.push(['LPAREN','(',line]); i++; continue; }
    if(c===')'){ tokens.push(['RPAREN',')',line]); i++; continue; }
    if(c===','){ tokens.push(['COMMA',',',line]); i++; continue; }
    if(c===':'){ tokens.push(['COLON',':',line]); i++; continue; }
    if(isAlpha(c)){
      let j=i; while(j<n&&isAlnum(src[j])) j++;
      const text=src.slice(i,j); const upper=text.toUpperCase();
      tokens.push([KEYWORDS.has(upper)?upper:'NAME', text, line]);
      i=j; continue;
    }
    throw new PseudoError(`Unexpected character '${c}' on line ${line}`);
  }
  tokens.push(['EOF','',line]);
  return tokens;
}

const BLOCK_ENDERS = new Set(['ELSE','ELSEIF','ENDIF','ENDWHILE','UNTIL','ENDFOR','ENDFUNCTION','ENDPROCEDURE','EOF']);

class Parser {
  constructor(tokens){ this.toks=tokens; this.pos=0; }
  peek(){ return this.toks[this.pos]; }
  at(...types){ return types.includes(this.toks[this.pos][0]); }
  advance(){ return this.toks[this.pos++]; }
  expect(t){ const tok=this.toks[this.pos]; if(tok[0]!==t) throw new PseudoError(`Line ${tok[2]}: expected ${t}, got ${tok[0]} (${tok[1]})`); this.pos++; return tok; }
  skipNewlines(){ while(this.at('NEWLINE')) this.pos++; }
  parseProgram(){ const stmts=[]; this.skipNewlines(); while(!this.at('EOF')){ stmts.push(this.parseStatement()); this.skipNewlines(); } return stmts; }
  parseBlock(stop){ const stmts=[]; this.skipNewlines(); while(!stop.has(this.peek()[0])){ stmts.push(this.parseStatement()); this.skipNewlines(); } return stmts; }
  parseStatement(){
    const t=this.peek()[0];
    if(t==='FUNCTION'||t==='PROCEDURE') return this.parseFuncdef();
    if(t==='IF') return this.parseIf();
    if(t==='WHILE') return this.parseWhile();
    if(t==='REPEAT') return this.parseRepeat();
    if(t==='FOR') return this.parseFor();
    if(t==='RETURN') return this.parseReturn();
    if(t==='OUTPUT'||t==='PRINT') return this.parseOutput();
    return this.parseAssignOrExpr();
  }
  parseFuncdef(){
    const endKw = this.peek()[0]==='FUNCTION' ? 'ENDFUNCTION' : 'ENDPROCEDURE';
    this.advance();
    const name=this.expect('NAME')[1];
    this.expect('LPAREN');
    const params=[];
    if(!this.at('RPAREN')){ params.push(this.expect('NAME')[1]); while(this.at('COMMA')){ this.advance(); params.push(this.expect('NAME')[1]); } }
    this.expect('RPAREN');
    const body=this.parseBlock(new Set([endKw,'EOF']));
    this.expect(endKw);
    return ['funcdef', name, params, body];
  }
  parseIf(){
    this.advance();
    const branches=[];
    let cond=this.parseExpr(); this.expect('THEN');
    let body=this.parseBlock(new Set(['ELSE','ELSEIF','ENDIF','EOF']));
    branches.push([cond,body]);
    while(this.at('ELSEIF')){
      this.advance(); const c2=this.parseExpr(); this.expect('THEN');
      const b2=this.parseBlock(new Set(['ELSE','ELSEIF','ENDIF','EOF']));
      branches.push([c2,b2]);
    }
    let elseBody=null;
    if(this.at('ELSE')){ this.advance(); elseBody=this.parseBlock(new Set(['ENDIF','EOF'])); }
    this.expect('ENDIF');
    return ['if', branches, elseBody];
  }
  parseWhile(){
    this.advance(); const cond=this.parseExpr();
    if(this.at('DO')) this.advance();
    const body=this.parseBlock(new Set(['ENDWHILE','EOF']));
    this.expect('ENDWHILE');
    return ['while', cond, body];
  }
  parseRepeat(){
    this.advance();
    const body=this.parseBlock(new Set(['UNTIL','EOF']));
    this.expect('UNTIL');
    const cond=this.parseExpr();
    return ['repeat', body, cond];
  }
  parseFor(){
    this.advance();
    const varName=this.expect('NAME')[1];
    if(this.at('=')||this.at('<-')) this.advance(); else this.expect('=');
    const startE=this.parseExpr();
    this.expect('TO');
    const endE=this.parseExpr();
    let stepE=null;
    if(this.at('STEP')){ this.advance(); stepE=this.parseExpr(); }
    const body=this.parseBlock(new Set(['ENDFOR','EOF']));
    this.expect('ENDFOR');
    return ['for', varName, startE, endE, stepE, body];
  }
  parseReturn(){
    this.advance();
    if(this.at('NEWLINE','EOF')||BLOCK_ENDERS.has(this.peek()[0])) return ['return', null];
    return ['return', this.parseExpr()];
  }
  parseOutput(){
    this.advance();
    const exprs=[this.parseExpr()];
    while(this.at('COMMA')){ this.advance(); exprs.push(this.parseExpr()); }
    return ['output', exprs];
  }
  parseAssignOrExpr(){
    const expr=this.parseExpr();
    if(this.at('=','<-')){
      this.advance();
      if(expr[0]!=='var'&&expr[0]!=='index') throw new PseudoError('Left-hand side of assignment must be a variable');
      const rhs=this.parseExpr();
      return ['assign', expr, rhs];
    }
    return ['exprstmt', expr];
  }
  parseExpr(){ return this.parseOr(); }
  parseOr(){ let node=this.parseAnd(); while(this.at('OR')){ this.advance(); node=['binop','OR',node,this.parseAnd()]; } return node; }
  parseAnd(){ let node=this.parseNot(); while(this.at('AND')){ this.advance(); node=['binop','AND',node,this.parseNot()]; } return node; }
  parseNot(){ if(this.at('NOT')){ this.advance(); return ['unary','NOT',this.parseNot()]; } return this.parseComparison(); }
  parseComparison(){ let node=this.parseAdditive(); while(this.at('==','!=','<','>','<=','>=')){ const op=this.advance()[0]; node=['binop',op,node,this.parseAdditive()]; } return node; }
  parseAdditive(){ let node=this.parseMultiplicative(); while(this.at('+','-')){ const op=this.advance()[0]; node=['binop',op,node,this.parseMultiplicative()]; } return node; }
  parseMultiplicative(){ let node=this.parseUnary(); while(this.at('*','/','MOD','DIV')){ const op=this.advance()[0]; node=['binop',op,node,this.parseUnary()]; } return node; }
  parseUnary(){ if(this.at('-')){ this.advance(); return ['unary','-',this.parseUnary()]; } return this.parsePostfix(); }
  parsePostfix(){ let node=this.parsePrimary(); while(this.at('LBRACKET')){ this.advance(); const idx=this.parseExpr(); this.expect('RBRACKET'); node=['index',node,idx]; } return node; }
  parsePrimary(){
    const t=this.peek();
    if(t[0]==='NUMBER'){ this.advance(); return ['num', t[1]]; }
    if(t[0]==='STRING'){ this.advance(); return ['str', t[1]]; }
    if(t[0]==='TRUE'){ this.advance(); return ['bool', true]; }
    if(t[0]==='FALSE'){ this.advance(); return ['bool', false]; }
    if(t[0]==='LPAREN'){ this.advance(); const e=this.parseExpr(); this.expect('RPAREN'); return e; }
    if(t[0]==='LBRACKET'){
      this.advance(); const elems=[];
      if(!this.at('RBRACKET')){ elems.push(this.parseExpr()); while(this.at('COMMA')){ this.advance(); elems.push(this.parseExpr()); } }
      this.expect('RBRACKET'); return ['arraylit', elems];
    }
    if(t[0]==='LBRACE'){
      this.advance(); const pairs=[];
      if(!this.at('RBRACE')){
        let k=this.parseExpr(); this.expect('COLON'); let v=this.parseExpr(); pairs.push([k,v]);
        while(this.at('COMMA')){ this.advance(); let k2=this.parseExpr(); this.expect('COLON'); let v2=this.parseExpr(); pairs.push([k2,v2]); }
      }
      this.expect('RBRACE'); return ['dictlit', pairs];
    }
    if(t[0]==='NAME'){
      this.advance(); const name=t[1];
      if(this.at('LPAREN')){
        this.advance(); const args=[];
        if(!this.at('RPAREN')){ args.push(this.parseExpr()); while(this.at('COMMA')){ this.advance(); args.push(this.parseExpr()); } }
        this.expect('RPAREN'); return ['call', name, args];
      }
      return ['var', name];
    }
    throw new PseudoError(`Line ${t[2]}: unexpected token ${t[0]} (${t[1]})`);
  }
}

function parse(src){ return new Parser(tokenize(src)).parseProgram(); }

function truthy(v){
  if(v===0||v===''||v===false||v===null||v===undefined) return false;
  if(Array.isArray(v)) return v.length>0;
  if(v instanceof Map) return v.size>0;
  return true;
}

function deepEqual(a,b){
  if(a instanceof Map || b instanceof Map){
    if(!(a instanceof Map) || !(b instanceof Map)) return false;
    if(a.size!==b.size) return false;
    for(const [k,v] of a) if(!b.has(k)||!deepEqual(v,b.get(k))) return false;
    return true;
  }
  if(Array.isArray(a)||Array.isArray(b)){
    if(!Array.isArray(a)||!Array.isArray(b)||a.length!==b.length) return false;
    for(let i=0;i<a.length;i++) if(!deepEqual(a[i],b[i])) return false;
    return true;
  }
  return a===b;
}

function pymod(a,b){ return ((a%b)+b)%b; }

function applyBinop(op,l,r){
  switch(op){
    case '+': if(Array.isArray(l)&&Array.isArray(r)) return l.concat(r); return l+r;
    case '-': return l-r;
    case '*': return l*r;
    case '/': return l/r;
    case 'MOD': return pymod(l,r);
    case 'DIV': return Math.floor(l/r);
    case '==': return deepEqual(l,r);
    case '!=': return !deepEqual(l,r);
    case '<': return l<r;
    case '>': return l>r;
    case '<=': return l<=r;
    case '>=': return l>=r;
    default: throw new PseudoError(`Unknown operator ${op}`);
  }
}

class PseudoInterp {
  constructor(programStmts, opts={}){
    this.funcs={}; this.globals={}; this.steps=0;
    this.maxSteps = opts.maxSteps || 200000;
    this.timeoutMs = opts.timeoutMs || 2000;
    this.start = null;
    const prelude=[];
    for(const stmt of programStmts){
      if(stmt[0]==='funcdef'){ this.funcs[stmt[1].toUpperCase()]=[stmt[2], stmt[3]]; }
      else prelude.push(stmt);
    }
    this._prelude=prelude;
  }
  runPrelude(){ this.start=Date.now(); this.execBlock(this._prelude, this.globals); }
  call(name,args){ if(this.start===null) this.start=Date.now(); return this.callAny(name, args.slice()); }
  tick(){
    this.steps++;
    if(this.steps>this.maxSteps) throw new PseudoError('Too many steps (possible infinite loop)');
    if(this.steps%2000===0 && Date.now()-this.start>this.timeoutMs) throw new PseudoError('Timed out (possible infinite loop)');
  }
  execBlock(stmts,scope){ for(const s of stmts) this.execStmt(s,scope); }
  execStmt(stmt,scope){
    this.tick();
    const tag=stmt[0];
    if(tag==='assign'){ const val=this.eval(stmt[2],scope); this.assignTarget(stmt[1],val,scope); }
    else if(tag==='if'){
      for(const [cond,body] of stmt[1]){ if(truthy(this.eval(cond,scope))){ this.execBlock(body,scope); return; } }
      if(stmt[2]!==null) this.execBlock(stmt[2],scope);
    }
    else if(tag==='while'){ while(truthy(this.eval(stmt[1],scope))){ this.execBlock(stmt[2],scope); this.tick(); } }
    else if(tag==='repeat'){ while(true){ this.execBlock(stmt[1],scope); this.tick(); if(truthy(this.eval(stmt[2],scope))) break; } }
    else if(tag==='for'){
      const [,varName,startE,endE,stepE,body]=stmt;
      let i=this.eval(startE,scope); const endV=this.eval(endE,scope);
      const stepV = stepE!==null ? this.eval(stepE,scope) : 1;
      if(stepV===0) throw new PseudoError('FOR step cannot be 0');
      while((stepV>0 && i<=endV) || (stepV<0 && i>=endV)){
        scope[varName]=i; this.execBlock(body,scope); i+=stepV; this.tick();
      }
    }
    else if(tag==='return'){ throw new ReturnSignal(stmt[1]!==null ? this.eval(stmt[1],scope) : null); }
    else if(tag==='output'){ for(const e of stmt[1]) this.eval(e,scope); }
    else if(tag==='exprstmt'){ this.eval(stmt[1],scope); }
    else throw new PseudoError(`Unknown statement '${tag}'`);
  }
  getContainerRef(node,scope){
    if(node[0]==='var'){ if(!(node[1] in scope)) scope[node[1]]=[]; return scope[node[1]]; }
    if(node[0]==='index'){
      const base=this.getContainerRef(node[1],scope); const idx=this.eval(node[2],scope);
      if(base instanceof Map){ if(!base.has(idx)) base.set(idx,[]); return base.get(idx); }
      if(Array.isArray(base)){ const i=Math.trunc(idx); while(i>=base.length) base.push([]); return base[i]; }
      throw new PseudoError('Cannot index into this value');
    }
    throw new PseudoError('Invalid assignment target');
  }
  assignTarget(target,value,scope){
    if(target[0]==='var'){ scope[target[1]]=value; }
    else if(target[0]==='index'){
      const container=this.getContainerRef(target[1],scope); const idxVal=this.eval(target[2],scope);
      if(container instanceof Map){ container.set(idxVal,value); }
      else if(Array.isArray(container)){ const i=Math.trunc(idxVal); while(i>=container.length) container.push(null); container[i]=value; }
      else throw new PseudoError('Cannot index-assign into this value');
    } else throw new PseudoError('Invalid assignment target');
  }
  eval(node,scope){
    const tag=node[0];
    if(tag==='num'||tag==='str'||tag==='bool') return node[1];
    if(tag==='arraylit') return node[1].map(e=>this.eval(e,scope));
    if(tag==='dictlit'){ const m=new Map(); for(const [k,v] of node[1]) m.set(this.eval(k,scope), this.eval(v,scope)); return m; }
    if(tag==='var'){ if(node[1] in scope) return scope[node[1]]; if(node[1] in this.globals) return this.globals[node[1]]; throw new PseudoError(`Undefined variable '${node[1]}'`); }
    if(tag==='index'){
      const base=this.eval(node[1],scope); const idx=this.eval(node[2],scope);
      if(base instanceof Map){ if(!base.has(idx)) throw new PseudoError(`Key ${JSON.stringify(idx)} not found`); return base.get(idx); }
      if(Array.isArray(base)||typeof base==='string'){ const i=Math.trunc(idx); const v=base[i]; if(v===undefined) throw new PseudoError(`Index ${i} out of range`); return v; }
      throw new PseudoError('Cannot index this value');
    }
    if(tag==='binop'){
      const op=node[1];
      if(op==='AND') return truthy(this.eval(node[2],scope)) && truthy(this.eval(node[3],scope));
      if(op==='OR') return truthy(this.eval(node[2],scope)) || truthy(this.eval(node[3],scope));
      return applyBinop(op, this.eval(node[2],scope), this.eval(node[3],scope));
    }
    if(tag==='unary'){
      const v=this.eval(node[2],scope);
      if(node[1]==='-') return -v;
      if(node[1]==='NOT') return !truthy(v);
      throw new PseudoError('Bad unary operator');
    }
    if(tag==='call') return this.callAny(node[1], node[2].map(a=>this.eval(a,scope)));
    throw new PseudoError(`Cannot evaluate node '${tag}'`);
  }
  callAny(name,args){
    const key=name.toUpperCase();
    if(this.funcs[key]){
      const [params,body]=this.funcs[key]; const scope={};
      params.forEach((p,i)=>{ scope[p]=args[i]; });
      try{ this.execBlock(body,scope); } catch(e){ if(e instanceof ReturnSignal) return e.value; throw e; }
      return null;
    }
    const a=args;
    switch(key){
      case 'LENGTH': return (a[0] instanceof Map) ? a[0].size : a[0].length;
      case 'APPEND': return a[0].concat([a[1]]);
      case 'ABS': return Math.abs(a[0]);
      case 'ROUND': { const n=a[1]; if(n===undefined) return Math.round(a[0]); const f=Math.pow(10,n); return Math.round((a[0]+Number.EPSILON)*f)/f; }
      case 'INT': return typeof a[0]==='string' ? parseInt(a[0],10) : Math.trunc(a[0]);
      case 'STR': return toStr(a[0]);
      case 'FLOAT': return typeof a[0]==='string' ? parseFloat(a[0]) : Number(a[0]);
      case 'MAX': return a.length>1 ? Math.max(...a) : Math.max(...a[0]);
      case 'MIN': return a.length>1 ? Math.min(...a) : Math.min(...a[0]);
      case 'UPPER': return String(a[0]).toUpperCase();
      case 'LOWER': return String(a[0]).toLowerCase();
      case 'CONCAT': return a.map(toStr).join('');
      case 'CONTAINS': {
        const [container,item]=a;
        if(container instanceof Map) return container.has(item);
        if(typeof container==='string') return container.includes(item);
        if(Array.isArray(container)) return container.some(x=>deepEqual(x,item));
        return false;
      }
      case 'KEYS': return Array.from(a[0].keys());
      case 'SORTED': { const arr=a[0].slice(); arr.sort((x,y)=> x<y?-1:x>y?1:0); return arr; }
      case 'LIST': return Array.isArray(a[0]) ? a[0].slice() : Array.from(a[0]);
      default: throw new PseudoError(`Unknown function '${name}'`);
    }
  }
}

function toStr(v){
  if(v===null||v===undefined) return 'None';
  if(typeof v==='boolean') return v?'True':'False';
  if(Array.isArray(v)) return '['+v.map(toStr2).join(', ')+']';
  if(v instanceof Map) return '{'+Array.from(v.entries()).map(([k,val])=>toStr2(k)+': '+toStr2(val)).join(', ')+'}';
  return String(v);
}
function toStr2(v){ if(typeof v==='string') return `'${v}'`; return toStr(v); }

function runPseudocode(source, funcName, args){
  const stmts = parse(source);
  const interp = new PseudoInterp(stmts, {});
  interp.runPrelude();
  if(!interp.funcs[funcName.toUpperCase()]) throw new PseudoError(`Your code must define a function named '${funcName}'.`);
  return interp.call(funcName, args);
}

// ===================== Python-subset -> Pseudocode transpiler =====================
function splitTopLevelArgs(s){
  let depth=0, cur='', res=[];
  for(const ch of s){
    if('([{'.includes(ch)) depth++;
    if(')]}'.includes(ch)) depth--;
    if(ch===','&&depth===0){ res.push(cur); cur=''; } else cur+=ch;
  }
  if(cur.trim()!=='') res.push(cur);
  return res.map(x=>x.trim());
}

function exprSub(e){
  const strs=[];
  let out = e.replace(/'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*"/g, m=>{ strs.push(m); return `\u0001${strs.length-1}\u0002`; });
  out = out.replace(/\bTrue\b/g,'TRUE').replace(/\bFalse\b/g,'FALSE').replace(/\bNone\b/g,'0');
  out = out.replace(/\band\b/g,'AND').replace(/\bor\b/g,'OR').replace(/\bnot\b/g,'NOT ');
  // `X in Y` (not part of a for-loop, already handled separately) -> CONTAINS(Y, X)
  out = out.replace(/^(.*?)\bin\b(.*)$/, (whole,l,r)=>{
    if(/\bfor\b/.test(whole)) return whole; // safety, shouldn't occur here
    const lt=l.trim(), rt=r.trim();
    if(lt==='' || rt==='') return whole;
    return `CONTAINS(${rt}, ${lt})`;
  });
  out = out.replace(/\blen\(/g,'LENGTH(');
  out = out.replace(/\bstr\(/g,'STR(').replace(/\bint\(/g,'INT(').replace(/\bfloat\(/g,'FLOAT(');
  out = out.replace(/\babs\(/g,'ABS(').replace(/\bround\(/g,'ROUND(');
  out = out.replace(/\bmax\(/g,'MAX(').replace(/\bmin\(/g,'MIN(');
  out = out.replace(/\bsorted\(/g,'SORTED(');
  out = out.replace(/\blist\(/g,'LIST(');
  out = out.replace(/\/\//g,' DIV ');
  out = out.replace(/%/g,' MOD ');
  out = out.replace(/\u0001(\d+)\u0002/g, (m,i)=>strs[Number(i)]);
  return out;
}

function pyToPseudo(src){
  const rawLines = src.replace(/\t/g,'    ').split('\n');
  const lines=[];
  for(const raw of rawLines){
    if(raw.trim()==='') continue;
    const m = raw.match(/^( *)/);
    lines.push({indent:m[1].length, text: raw.slice(m[1].length)});
  }
  const out=[]; const stack=[];
  const closeKw={IF:'ENDIF', FOR:'ENDFOR', WHILE:'ENDWHILE', DEF:'ENDFUNCTION'};

  function transformLine(text){
    let m;
    if((m=text.match(/^print\s*\((.*)\)\s*$/))) return exprSub2Head(`OUTPUT ${m[1]}`);
    if((m=text.match(/^def\s+(\w+)\s*\((.*)\)\s*:\s*$/))) return {head:`FUNCTION ${m[1]}(${m[2]})`, kind:'DEF'};
    if((m=text.match(/^if\s+(.*):\s*$/))) return {head:`IF ${exprSub(m[1])} THEN`, kind:'IF'};
    if((m=text.match(/^elif\s+(.*):\s*$/))) return {head:`ELSEIF ${exprSub(m[1])} THEN`, kind:null};
    if(/^else\s*:\s*$/.test(text)) return {head:'ELSE', kind:null};
    if((m=text.match(/^while\s+(.*):\s*$/))) return {head:`WHILE ${exprSub(m[1])}`, kind:'WHILE'};
    if((m=text.match(/^for\s+(\w+)\s+in\s+range\s*\((.*)\)\s*:\s*$/))){
      const varName=m[1]; const parts=splitTopLevelArgs(m[2]);
      let startE,endE,stepE=null;
      if(parts.length===1){ startE='0'; endE=`(${parts[0]})-1`; }
      else if(parts.length===2){ startE=parts[0]; endE=`(${parts[1]})-1`; }
      else { startE=parts[0]; stepE=parts[2]; endE = stepE.trim().startsWith('-') ? `(${parts[1]})+1` : `(${parts[1]})-1`; }
      let head=`FOR ${varName} = ${exprSub(startE)} TO ${exprSub(endE)}`;
      if(stepE) head += ` STEP ${exprSub(stepE)}`;
      return {head, kind:'FOR'};
    }
    if((m=text.match(/^for\s+(\w+)\s+in\s+(.*)\s*:\s*$/))){
      const varName=m[1]; const iterExpr=exprSub(m[2]); const idx='__i_'+varName;
      return {head:`FOR ${idx} = 0 TO LENGTH(${iterExpr}) - 1`, extra:`${varName} = ${iterExpr}[${idx}]`, kind:'FOR'};
    }
    if(/^return\s*$/.test(text)) return 'RETURN';
    if((m=text.match(/^return\s+(.*)$/))) return 'RETURN ' + exprSub(m[1]);
    if((m=text.match(/^([\w\[\]]+)\.append\s*\((.*)\)\s*$/))) return `${m[1]} = APPEND(${m[1]}, ${exprSub(m[2])})`;
    return exprSub(text);
  }
  function exprSub2Head(s){ return s.replace(/^OUTPUT\s+(.*)$/, (mm,g)=>'OUTPUT '+exprSub(g)); }

  for(const {indent,text} of lines){
    const isElifElse = /^elif\b/.test(text) || /^else\s*:/.test(text);
    while(stack.length){
      const top = stack[stack.length-1];
      if(indent < top.indent){ out.push(closeKw[stack.pop().kind]); continue; }
      if(indent === top.indent){
        if(isElifElse && top.kind==='IF') break;
        out.push(closeKw[stack.pop().kind]); continue;
      }
      break;
    }
    const tr = transformLine(text);
    if(typeof tr==='string') out.push(tr);
    else { out.push(tr.head); if(tr.extra) out.push(tr.extra); if(tr.kind) stack.push({indent, kind:tr.kind}); }
  }
  while(stack.length) out.push(closeKw[stack.pop().kind]);
  return out.join('\n');
}

function runPython(source, funcName, args){
  const pc = pyToPseudo(source);
  return runPseudocode(pc, funcName, args);
}

module.exports = { runPseudocode, runPython, pyToPseudo, deepEqual, PseudoError };