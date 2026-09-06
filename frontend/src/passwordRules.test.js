// The password rules the registration screen shows, and the generated example.
//
// These must agree with backend/password_policy.py: the server is the
// authority, and a browser that showed a green tick for something the server
// then refuses would be worse than showing nothing.
import test from 'node:test';
import assert from 'node:assert/strict';

import {
    PASSWORD_RULES,
    evaluatePassword,
    satisfiesAllRules,
    generateExamplePassword,
    MIN_LENGTH,
    MIN_UPPERCASE,
    MIN_DIGITS,
    MIN_SPECIALS,
} from './passwordRules.js';

test('the thresholds match the server policy', () => {
    assert.equal(MIN_LENGTH, 12);
    assert.equal(MIN_UPPERCASE, 1);
    assert.equal(MIN_DIGITS, 2);
    assert.equal(MIN_SPECIALS, 2);
});

test('there are exactly four rules, in the order the screen lists them', () => {
    assert.deepEqual(PASSWORD_RULES.map(rule => rule.id),
        ['length', 'uppercase', 'digits', 'specials']);
});

test('every rule label is French and names its threshold', () => {
    const labels = PASSWORD_RULES.map(rule => rule.label);
    assert.match(labels[0], /au moins 12 caractères/);
    assert.match(labels[1], /au moins 1 majuscule/);
    assert.match(labels[2], /au moins 2 chiffres/);
    assert.match(labels[3], /au moins 2 caractères spéciaux/);
});

test('each rule fails on its own boundary and passes one character later', () => {
    // length: 11 vs 12
    assert.equal(evaluatePassword('Abcde12!!xy').length, false);
    assert.equal(evaluatePassword('Abcde12!!xyz').length, true);

    // uppercase: 0 vs 1
    assert.equal(evaluatePassword('abcdefghij12!!').uppercase, false);
    assert.equal(evaluatePassword('Abcdefghij12!!').uppercase, true);

    // digits: 1 vs 2
    assert.equal(evaluatePassword('Abcdefghij1!!').digits, false);
    assert.equal(evaluatePassword('Abcdefghij12!!').digits, true);

    // specials: 1 vs 2
    assert.equal(evaluatePassword('Abcdefghij12!').specials, false);
    assert.equal(evaluatePassword('Abcdefghij12!?').specials, true);
});

test('only the rule concerned flips', () => {
    const before = evaluatePassword('abcdefghijkl');
    assert.deepEqual(before, { length: true, uppercase: false, digits: false, specials: false });
    const after = evaluatePassword('Abcdefghijkl');
    assert.deepEqual(after, { length: true, uppercase: true, digits: false, specials: false });
});

test('an accented capital counts as an uppercase letter', () => {
    // \p{Lu} rather than A-Z: « École » must not be told it has no capital.
    assert.equal(evaluatePassword('École12!!abcd').uppercase, true);
});

test('an accented letter is not mistaken for a special character', () => {
    assert.equal(evaluatePassword('Écolé123abcde').specials, false);
});

test('a non-string is handled without throwing', () => {
    for (const value of [undefined, null, 0, {}, []]) {
        assert.deepEqual(evaluatePassword(value),
            { length: false, uppercase: false, digits: false, specials: false });
    }
});

test('satisfiesAllRules agrees with the individual rules', () => {
    assert.equal(satisfiesAllRules('Abcdefghij12!?'), true);
    assert.equal(satisfiesAllRules('Abcdefghij12!'), false);
});

test('the generated example always satisfies every rule', () => {
    // 500 draws: a generator that is right most of the time is not right.
    for (let i = 0; i < 500; i++) {
        const example = generateExamplePassword();
        assert.ok(satisfiesAllRules(example),
            `generated example does not satisfy the policy it illustrates: ${example}`);
    }
});

test('the example is not a fixed string', () => {
    const seen = new Set();
    for (let i = 0; i < 50; i++) seen.add(generateExamplePassword());
    // Whatever a public app prints as an example, users type verbatim — a
    // constant would be a known credential on every account that copied it.
    assert.ok(seen.size > 1, 'generateExamplePassword() returned a constant');
});

test('the example never repeats the same word twice', () => {
    for (let i = 0; i < 200; i++) {
        const example = generateExamplePassword();
        const words = example.match(/\p{Lu}\p{Ll}+/gu) || [];
        assert.equal(new Set(words).size, words.length, `repeated word in ${example}`);
    }
});
