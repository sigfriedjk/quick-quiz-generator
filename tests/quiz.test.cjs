const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { runInNewContext } = require('node:vm');
const html = readFileSync(require('node:path').join(__dirname, '../index.html'), 'utf8');
const source = html.match(/<script id="quiz-logic">([\s\S]*?)<\/script>/)[1];
const api = runInNewContext(source + '\n({mathProblem, musicProblem, staffPosition, ledgerLines})');
test('all supported digit pairs produce correctly sized operands and exact division', () => {
 for (const type of ['addition', 'subtraction', 'multiplication', 'division']) {
  for (let first = 1; first <= 4; first++) for (let second = 1; second <= 4; second++) {
   if (type === 'division' && second > first) {
    assert.throws(() => api.mathProblem(type, first, second), /second number/);
    continue;
   }
   for (let i = 0; i < 100; i++) {
    const { a, b } = api.mathProblem(type, first, second);
    assert.equal(String(a).length, first);
    assert.equal(String(b).length, second);
    if (type === 'division') assert.equal(a % b, 0);
   }
  }
 }
});
test('invalid inputs are rejected', () => {
 for (const digits of [0, 5, -1, 1.5, NaN]) assert.throws(() => api.mathProblem('addition', digits, 1));
 assert.throws(() => api.mathProblem('unknown', 1, 1));
 assert.throws(() => api.musicProblem('unknown'));
});
test('music notes use selected clefs and two registers', () => {
 for (const selection of ['treble', 'bass', 'mixed']) {
  const clefs = new Set();
  for (let i = 0; i < 500; i++) {
   const note = api.musicProblem(selection);
   assert.ok(['C', 'D', 'E', 'F', 'G'].includes(note.letter));
   assert.ok((note.clef === 'treble' ? [4, 5] : [2, 3]).includes(note.octave));
   if (selection !== 'mixed') assert.equal(note.clef, selection);
   clefs.add(note.clef);
  }
  assert.equal(clefs.size, selection === 'mixed' ? 2 : 1);
 }
});
test('staff anchors and ledger lines match standard notation', () => {
 assert.equal(api.staffPosition('E', 4, 'treble'), 54);
 assert.equal(api.staffPosition('G', 2, 'bass'), 54);
 assert.equal(api.staffPosition('C', 4, 'treble'), 62);
 assert.equal(api.staffPosition('C', 2, 'bass'), 70);
 assert.deepEqual(Array.from(api.ledgerLines(70)), [62, 70]);
 assert.deepEqual(Array.from(api.ledgerLines(10)), [14]);
 assert.deepEqual(Array.from(api.ledgerLines(38)), []);
});
