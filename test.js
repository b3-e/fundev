const { runPseudocode, runPython, pyToPseudo, deepEqual } = require('./engine.js');

let pass=0, fail=0;
function norm(v){
  if(v instanceof Map) return Object.fromEntries(Array.from(v.entries()).map(([k,val])=>[String(k), norm(val)]));
  if(Array.isArray(v)) return v.map(norm);
  return v;
}
function check(label, actual, expected){
  const a=norm(actual), e=norm(expected);
  if(JSON.stringify(a)===JSON.stringify(e)){ pass++; }
  else { fail++; console.log('FAIL', label, 'got', JSON.stringify(a), 'want', JSON.stringify(e)); }
}

function checkThrows(label, fn, expectedSubstring){
  try {
    fn();
    fail++;
    console.log('FAIL', label, 'did not throw');
  } catch (err) {
    const msg = String(err && err.message ? err.message : err);
    if(expectedSubstring && !msg.toLowerCase().includes(expectedSubstring.toLowerCase())){
      fail++;
      console.log('FAIL', label, 'wrong error', msg);
      return;
    }
    pass++;
  }
}

// Pseudocode tests
check('pc rectangle', runPseudocode(`FUNCTION rectangle_area(length, width)\n    RETURN length * width\nENDFUNCTION\n`, 'rectangle_area', [4,5]), 20);

check('pc grade', runPseudocode(`FUNCTION grade_from_score(score)\n IF score >= 80 THEN\n RETURN "A"\n ELSEIF score >= 70 THEN\n RETURN "B"\n ELSE\n RETURN "E"\n ENDIF\nENDFUNCTION\n`, 'grade_from_score',[95]), "A");

check('pc leap', runPseudocode(`FUNCTION is_leap_year(year)\n RETURN (year MOD 4 == 0) AND ((NOT (year MOD 100 == 0)) OR (year MOD 400 == 0))\nENDFUNCTION\n`,'is_leap_year',[2000]), true);

check('pc sum_first_n', runPseudocode(`FUNCTION sum_first_n(n)\n total = 0\n FOR i = 1 TO n\n total = total + i\n ENDFOR\n RETURN total\nENDFUNCTION\n`,'sum_first_n',[5]), 15);

check('pc reverse_array', runPseudocode(`FUNCTION reverse_array(arr)\n result = []\n i = LENGTH(arr) - 1\n WHILE i >= 0\n result[LENGTH(result)] = arr[i]\n i = i - 1\n ENDWHILE\n RETURN result\nENDFUNCTION\n`,'reverse_array',[[1,2,3]]), [3,2,1]);

check('pc word_freq', runPseudocode(`FUNCTION word_frequency(words)\n freq = {}\n FOR i = 0 TO LENGTH(words) - 1\n w = words[i]\n IF CONTAINS(freq, w) THEN\n freq[w] = freq[w] + 1\n ELSE\n freq[w] = 1\n ENDIF\n ENDFOR\n RETURN freq\nENDFUNCTION\n`,'word_frequency',[["cat","dog","cat"]]), {cat:2, dog:1});

check('pc invert_dict', runPseudocode(`FUNCTION invert_dictionary(d)\n result = {}\n k2 = KEYS(d)\n FOR i = 0 TO LENGTH(k2) - 1\n result[d[k2[i]]] = k2[i]\n ENDFOR\n RETURN result\nENDFUNCTION\n`,'invert_dictionary',[new Map([['a',1],['b',2]])]), new Map([[1,'a'],[2,'b']]));

check('pc binary_search', runPseudocode(`FUNCTION binary_search(arr, target)\n lo = 0\n hi = LENGTH(arr) - 1\n WHILE lo <= hi\n mid = (lo + hi) DIV 2\n IF arr[mid] == target THEN\n RETURN mid\n ELSEIF arr[mid] < target THEN\n lo = mid + 1\n ELSE\n hi = mid - 1\n ENDIF\n ENDWHILE\n RETURN -1\nENDFUNCTION\n`,'binary_search',[[1,3,5,7,9,11],7]), 3);

check('pc factorial recursive', runPseudocode(`FUNCTION factorial_recursive(n)\n IF n <= 1 THEN\n RETURN 1\n ENDIF\n RETURN n * factorial_recursive(n - 1)\nENDFUNCTION\n`,'factorial_recursive',[5]), 120);

check('pc repeat until', runPseudocode(`FUNCTION count_to(n)\n i = 0\n REPEAT\n i = i + 1\n UNTIL i >= n\n RETURN i\nENDFUNCTION\n`,'count_to',[5]), 5);

// Python transpile tests
console.log('--- transpile samples ---');
console.log(pyToPseudo(`def grade_from_score(score):\n    if score >= 80:\n        return 'A'\n    elif score >= 70:\n        return 'B'\n    else:\n        return 'E'\n`));
console.log('---');
console.log(pyToPseudo(`def sum_first_n(n):\n    total = 0\n    for i in range(1, n + 1):\n        total = total + i\n    return total\n`));
console.log('---');
console.log(pyToPseudo(`def append_bonus(scores):\n    scores.append(99)\n    return scores\n`));
console.log('---');
console.log(pyToPseudo(`def find_max(arr):\n    best = arr[0]\n    for x in arr:\n        if x > best:\n            best = x\n    return best\n`));

check('py grade', runPython(`def grade_from_score(score):\n    if score >= 80:\n        return 'A'\n    elif score >= 70:\n        return 'B'\n    else:\n        return 'E'\n`, 'grade_from_score', [95]), 'A');

check('py sum_first_n', runPython(`def sum_first_n(n):\n    total = 0\n    for i in range(1, n + 1):\n        total = total + i\n    return total\n`, 'sum_first_n', [5]), 15);

check('py append_bonus', runPython(`def append_bonus(scores):\n    scores.append(99)\n    return scores\n`, 'append_bonus', [[1,2,3]]), [1,2,3,99]);

check('py find_max (for-in)', runPython(`def find_max(arr):\n    best = arr[0]\n    for x in arr:\n        if x > best:\n            best = x\n    return best\n`, 'find_max', [[3,7,2,9,4]]), 9);

check('py while collatz', runPython(`def collatz_steps(n):\n    steps = 0\n    while n != 1:\n        if n % 2 == 0:\n            n = n // 2\n        else:\n            n = 3 * n + 1\n        steps = steps + 1\n    return steps\n`, 'collatz_steps', [6]), 8);

check('py recursive fib', runPython(`def fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n`, 'fib', [10]), 55);

check('py bubble sort', runPython(`def bubble_sort(arr):\n    a = list(arr)\n    n = len(a)\n    for i in range(n):\n        for j in range(n - i - 1):\n            if a[j] > a[j + 1]:\n                temp = a[j]\n                a[j] = a[j + 1]\n                a[j + 1] = temp\n    return a\n`, 'bubble_sort', [[3,1,2]]), [1,2,3]);

check('py dict', runPython(`def word_frequency(words):\n    freq = {}\n    for w in words:\n        if w in freq:\n            freq[w] = freq[w] + 1\n        else:\n            freq[w] = 1\n    return freq\n`, 'word_frequency', [["cat","dog","cat"]]), {cat:2,dog:1});

console.log(`\n${pass} passed, ${fail} failed`);