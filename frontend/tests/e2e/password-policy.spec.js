// The registration screen's password rules: visible before typing, live as
// the user types, and an example that is generated rather than hardcoded.
//
// The rules themselves are enforced by the server (backend/password_policy.py,
// tests/test_password_policy.py). What is under test here is that the user is
// told what they are BEFORE being rejected for breaking them.
import { expect } from '@playwright/test';
import { test } from './test-base.js';
import { SELECTORS, APP_BASE } from '../helpers/index.js';

const RULES = ['length', 'uppercase', 'digits', 'specials'];

/** Opens « Créer un nouveau compte » from the login screen. */
async function openRegistration(page) {
    await page.goto(APP_BASE);
    await expect(page.locator(SELECTORS.loginForm)).toBeVisible();
    await page.getByRole('button', { name: 'Créer un compte' }).click();
    await expect(page.getByRole('heading', { name: 'Créer un nouveau compte' })).toBeVisible();
}

const passwordField = page => page.locator('input[name="password"]');
const rule = (page, id) => page.locator(`.sid-pwrules__item[data-rule="${id}"]`);

test.describe('Règles de mot de passe — inscription', () => {
    test('les quatre règles sont visibles avant toute saisie', async ({ page }) => {
        await openRegistration(page);

        await expect(page.locator('.sid-pwrules__intro'))
            .toHaveText('Votre mot de passe doit contenir :');
        for (const id of RULES) {
            await expect(rule(page, id), `la règle « ${id} » doit être visible d'emblée`).toBeVisible();
        }
        // Rien n'a été tapé : aucune règle n'est encore satisfaite.
        for (const id of RULES) {
            await expect(rule(page, id)).toHaveAttribute('data-satisfied', 'false');
        }
    });

    test('les règles sont énoncées en français, avec les bons seuils', async ({ page }) => {
        await openRegistration(page);
        const text = await page.locator('.sid-pwrules').innerText();
        expect(text).toContain('au moins 12 caractères');
        expect(text).toContain('au moins 1 majuscule');
        expect(text).toContain('au moins 2 chiffres');
        expect(text).toContain('au moins 2 caractères spéciaux');
    });

    test('chaque indicateur bascule quand sa règle — et elle seule — est remplie', async ({ page }) => {
        await openRegistration(page);
        const field = passwordField(page);

        // 12 caractères, rien d'autre : seule « length » passe.
        await field.fill('abcdefghijkl');
        await expect(rule(page, 'length')).toHaveAttribute('data-satisfied', 'true');
        await expect(rule(page, 'uppercase')).toHaveAttribute('data-satisfied', 'false');
        await expect(rule(page, 'digits')).toHaveAttribute('data-satisfied', 'false');
        await expect(rule(page, 'specials')).toHaveAttribute('data-satisfied', 'false');

        // + une majuscule.
        await field.fill('Abcdefghijkl');
        await expect(rule(page, 'uppercase')).toHaveAttribute('data-satisfied', 'true');
        await expect(rule(page, 'digits')).toHaveAttribute('data-satisfied', 'false');

        // + un seul chiffre : la règle en demande deux, elle ne bascule pas.
        await field.fill('Abcdefghijk1');
        await expect(rule(page, 'digits')).toHaveAttribute('data-satisfied', 'false');

        // + le deuxième chiffre.
        await field.fill('Abcdefghij12');
        await expect(rule(page, 'digits')).toHaveAttribute('data-satisfied', 'true');
        await expect(rule(page, 'specials')).toHaveAttribute('data-satisfied', 'false');

        // + un seul caractère spécial : toujours pas.
        await field.fill('Abcdefghij12!');
        await expect(rule(page, 'specials')).toHaveAttribute('data-satisfied', 'false');

        // + le second : les quatre sont vertes.
        await field.fill('Abcdefghij12!?');
        for (const id of RULES) {
            await expect(rule(page, id)).toHaveAttribute('data-satisfied', 'true');
        }
    });

    test('revenir en arrière repasse la règle au rouge', async ({ page }) => {
        await openRegistration(page);
        const field = passwordField(page);
        await field.fill('Abcdefghij12!?');
        await expect(rule(page, 'length')).toHaveAttribute('data-satisfied', 'true');
        await field.fill('Ab12!?');
        await expect(rule(page, 'length')).toHaveAttribute('data-satisfied', 'false');
    });

    test("un exemple est affiché, et il n'est pas le même deux fois", async ({ page }) => {
        // Ce qu'une application publique imprime comme exemple, des utilisateurs
        // le tapent tel quel : une chaîne figée serait un identifiant connu.
        await openRegistration(page);
        const first = await page.getByTestId('password-example').innerText();
        expect(first.length).toBeGreaterThanOrEqual(12);

        const seen = new Set([first]);
        for (let attempt = 0; attempt < 6; attempt++) {
            await page.reload();
            await page.getByRole('button', { name: 'Créer un compte' }).click();
            seen.add(await page.getByTestId('password-example').innerText());
        }
        expect(seen.size, "l'exemple doit être généré, pas codé en dur").toBeGreaterThan(1);
    });

    test("l'exemple est étiqueté comme un exemple à ne pas utiliser", async ({ page }) => {
        await openRegistration(page);
        await expect(page.locator('.sid-pwrules__warn'))
            .toContainText("n'utilisez pas ce mot de passe");
    });

    test("l'exemple affiché respecte lui-même la politique", async ({ page }) => {
        await openRegistration(page);
        const example = await page.getByTestId('password-example').innerText();
        await passwordField(page).fill(example);
        for (const id of RULES) {
            await expect(rule(page, id), `l'exemple viole la règle « ${id} »`)
                .toHaveAttribute('data-satisfied', 'true');
        }
    });

    test('un mot de passe non conforme affiche le message du serveur nommant la règle', async ({ page }) => {
        await openRegistration(page);
        await page.locator('input[name="first_name"]').fill('Jean');
        await page.locator('input[name="last_name"]').fill('Dupont');
        await page.locator('input[name="email"]').fill('jean.dupont@example.com');
        await page.locator('input[name="phone_number"]').fill('0600000000');
        await page.locator('input[name="user_name"]').fill('jdupont');
        await passwordField(page).fill('pw');

        await page.getByRole('button', { name: "S'inscrire" }).click();

        const alert = page.locator('.sid-alert--err');
        await expect(alert).toBeVisible();
        // Le message nomme la règle : « mot de passe invalide » rendrait le
        // formulaire inutilisable.
        await expect(alert).toContainText('12 caractères');
    });

    test('les règles tiennent dans un écran de 375 px sans débordement', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        await openRegistration(page);
        const overflow = await page.evaluate(() =>
            document.documentElement.scrollWidth - document.documentElement.clientWidth);
        expect(overflow).toBeLessThanOrEqual(0);
        await expect(page.locator('.sid-pwrules')).toBeVisible();
    });
});
