import js from '@eslint/js';
import globals from 'globals';

// AGENTS.md §5.7: nada de HTML armado como texto
const NO_HTML_STRINGS = [
  {
    selector: 'AssignmentExpression > MemberExpression[property.name=/^(innerHTML|outerHTML)$/]',
    message: 'Usar textContent o createElement (AGENTS.md §5.7).',
  },
  {
    selector:
      'CallExpression > MemberExpression[property.name=/^(insertAdjacentHTML|write|writeln)$/]',
    message: 'Usar createElement (AGENTS.md §5.7).',
  },
];

export default [
  { ignores: ['node_modules/', 'playwright-report/', 'test-results/'] },
  js.configs.recommended,
  {
    languageOptions: { globals: globals.browser },
    rules: { 'no-restricted-syntax': ['error', ...NO_HTML_STRINGS] },
  },
  {
    files: ['*.config.js', 'tests/**'],
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
  },
];
