// Expression bodies
var odds = evens.map(v => v + 1);
var nums = evens.map((v, i) => v + i);
var nums = evens.map(({v, i}) => v + i);
var nums = evens.map(([v, i]) => v + i);
var pairs = evens.map(v => ({even: v, odd: v + 1}));

const a = require('a');
__dirname, __filename;

module.exports = {};
exports = {};

// Statement bodies
nums.forEach(v => {
  if (v % 5 === 0)
    fives.push(v);
});

// Lexical this
var bob = {
  _name: "Bob",
  _friends: [],
  printFriends() {
    this._friends.forEach(f =>
      console.log(this._name + " knows " + f));
  }
}

class SkinnedMesh extends THREE.Mesh {
  constructor(geometry, materials) {
    super(geometry, materials);

    this.idMatrix = SkinnedMesh.defaultMatrix();
    this.bones = [];
    this.boneMatrices = [];
    //...
  }
  update(camera) {
    //...
    super.update();
  }
  get boneCount() {
    return this.bones.length;
  }
  set matrixType(matrixType) {
    this.idMatrix = SkinnedMesh[matrixType]();
  }
  static defaultMatrix() {
    return new THREE.Matrix4();
  }
}

var obj = {
    // __proto__
    __proto__: theProtoObj,
    // Shorthand for ‘handler: handler’
    handler,
    // Methods
    toString() {
     // Super calls
     return "d " + super.toString();
    },
    // Computed (dynamic) property names
    [ 'prop_' + (() => 42)() ]: 42
};


// Basic literal string creation
`In JavaScript '\n' is a line-feed.`

// Multiline strings
`In JavaScript this is
 not legal.`

// String interpolation
var name = "Bob", time = "today", foo = { bar: 1 };
`Hello ${name}, how are you ${time}, ${foo.bar} ${foo.bar()} ${path.join(1,2)}?`

foo.bar();
path.join(1,2);

// Construct an HTTP request prefix is used to interpret the replacements and construction
POST`http://foo.org/bar?a=${a}&b=${b}`(myOnReadyStateChangeHandler);

// Indented string interpolation
`<div>${[].map(() => {
  return `<div>${[].map(() => {
    return `<div>${[].map(() => {
      return `<div>${[].map(() => {
        return `<div></div>`;
      })}</div>`;
    })}</div>`;
  })}/div>`;
})}</div>`

// list matching
var [a, , b] = [1,2,3];

// object matching
var { op: a, lhs: { op: b }, rhs: c }
       = getASTNode()

// object matching shorthand
// binds `op`, `lhs` and `rhs` in scope
var {op, lhs, rhs} = getASTNode()

// Can be used in parameter position
function g({name: x}) {
  console.log(x);
}
g({name: 5})

// Fail-soft destructuring
var [a] = [];
a === undefined;

// Fail-soft destructuring with defaults
var [a = 1] = [];
a === 1;

function f(x, y=12) {
  // y is 12 if not passed (or passed as undefined)
  return x + y;
}
f(3) == 15

function f(x, ...y) {
  // y is an Array
  return x * y.length;
}
f(3, "hello", true) == 6

function f(x, y, z) {
  return x + y + z;
}
// Pass each elem of array as argument
f(...[1,2,3]) == 6

function f() {
  {
    let x;
    {
      // okay, block scoped name
      const x = "sneaky";
      // error, const
      x = "foo";
    }
    // error, already declared in block
    let x = "inner";
  }
}

let fibonacci = {
  [Symbol.iterator]() {
    let pre = 0, cur = 1;
    return {
      next() {
        [pre, cur] = [cur, pre + cur];
        return { done: false, value: cur }
      }
    }
  }
}

for (var n of fibonacci) {
  // truncate the sequence at 1000
  if (n > 1000)
    break;
  console.log(n);
}

var fibonacci = {
  [Symbol.iterator]: function*() {
    var pre = 0, cur = 1;
    for (;;) {
      var temp = pre;
      pre = cur;
      cur += temp;
      yield cur;
    }
  }
}

for (var n of fibonacci) {
  // truncate the sequence at 1000
  if (n > 1000)
    break;
  console.log(n);
}

// lib/math.js
export function sum(x, y) {
  return x + y;
}
export var pi = 3.141593;

export {
  sum,
  pi
};

// app.js
import * as math from "lib/math";
alert("2π = " + math.sum(math.pi, math.pi));

// otherApp.js
import {sum, pi} from "lib/math";
alert("2π = " + sum(pi, pi));

// lib/mathplusplus.js
export * from "lib/math";
export var e = 2.71828182846;
export default function(x) {
    return Math.log(x);
}

// app.js
import ln, {pi, e} from "lib/mathplusplus";
alert("2π = " + ln(e)*pi*2);

// Dynamic loading – ‘System’ is default loader
System.import('lib/math').then(function(m) {
  alert("2π = " + m.sum(m.pi, m.pi));
});

// Create execution sandboxes – new Loaders
var loader = new Loader({
  global: fixup(window) // replace ‘console.log’
});
loader.eval("console.log('hello world!');");

// Directly manipulate module cache
System.get('jquery');
System.set('jquery', Module({$: $})); // WARNING: not yet finalized

// Sets
var s = new Set();
s.add("hello").add("goodbye").add("hello");
s.size === 2;
s.has("hello") === true;

// Maps
var m = new Map();
m.set("hello", 42);
m.set(s, 34);
m.get(s) == 34;

// Weak Maps
var wm = new WeakMap();
wm.set(s, { extra: 42 });
wm.size === undefined

// Weak Sets
var ws = new WeakSet();
ws.add({ data: 42 });
// Because the added object has no other references, it will not be held in the set

// Proxying a normal object
var target = {};
var handler = {
  get: function (receiver, name) {
    return `Hello, ${name}!`;
  }
};

var p = new Proxy(target, handler);
p.world === 'Hello, world!';

// Proxying a function object
var target = function () { return 'I am the target'; };
var handler = {
  apply: function (receiver, ...args) {
    return 'I am the proxy';
  }
};

var p = new Proxy(target, handler);
p() === 'I am the proxy';

var MyClass = (function() {

  // module scoped symbol
  var key = Symbol("key");

  function MyClass(privateData) {
    this[key] = privateData;
  }

  MyClass.prototype = {
    doStuff: function() {
      return this[key];
    }
  };

  return MyClass;
})();

var c = new MyClass("hello")
c["key"] === undefined

// Pseudo-code of Array
class Array {
    constructor(...args) { /* ... */ }
    static [Symbol.create]() {
        // Install special [[DefineOwnProperty]]
        // to magically update 'length'
    }
}

// User code of Array subclass
class MyArray extends Array {
    constructor(...args) { super(...args); }
}

// Two-phase 'new':
// 1) Call @@create to allocate object
// 2) Invoke constructor on new instance
var arr = new MyArray();
arr[1] = 12;
arr.length == 2

function timeout(duration = 0) {
    return new Promise((resolve, reject) => {
        setTimeout(resolve, duration);
    })
}

var p = timeout(1000).then(() => {
    return timeout(2000);
}).then(() => {
    throw new Error("hmm");
}).catch(err => {
    return Promise.all([timeout(100), timeout(200)]);
})

async function main () {
  await foo();
}

const array = [...array];
const obj = {
  ...obj
}

/**
sample javascript from xui
*/

var foo = 1;
var bar = function(){
  return bar;
};

function foo(q,context){
  return true;
};

var foo = {
  bar: function () {
    return 1;
  },
  bad: () => {
    return 1;
  },
  baz: 1,
};

debugger;

o.foo();
o.bar = 1;
o.bar.baz = 1;

var undefined,
  xui,
  window     = this,
  string     = new String('string'),
  document   = window.document,
  simpleExpr = /^#?([\w-]+)$/,
  idExpr     = /^#/,
  tagExpr    = /<([\w:]+)/,
  slice      = function (e) { return [].slice.call(e, 0); };
  try { var a = slice(document.documentElement.childNodes)[0].nodeType; }
  catch(e){ slice = function (e) { var ret=[]; for (var i=0; e[i]; i++)
    ret.push(e[i]); return ret; }; }


window.x$ = window.xui = xui = function(q, context) {
  return new xui.fn.find(q, context);
};

console.log( 'string', params );

do
if
in
for
let
new
try
var
case
else
enum
eval
null
this
true
void
with
break
catch
class
const
false
super
throw
while
yield
delete
export
import
public
return
static
switch
typeof
default
extends
finally
package
private
continue
debugger
function
arguments
interface
protected
implements
instanceof
