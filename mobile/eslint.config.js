// eslint.config.js
// Configuración de ESLint 10.12.0 para Q-Wallet Mobile

module.exports = [
  {
    ignores: [
      "node_modules/**",
      ".expo/**",
      "dist/**",
      "web-build/**",
      "android/**",
      "ios/**",
      "**/*.d.ts",
      "**/*.ts",
      "**/*.tsx", // Type-checking y linting de TS/TSX es ejecutado por tsc --noEmit (strict: true). @typescript-eslint/parser queda como propuesta en BITACORA.md según límites de dependencias.
    ],
  },
  {
    files: ["**/*.js", "**/*.cjs", "**/*.mjs"],
    rules: {
      "no-unused-vars": "warn",
      "no-console": "error", // Seguro desde el diseño: cero console.log de datos sensibles
      "prefer-const": "error",
      "no-var": "error",
      "eqeqeq": ["error", "always"],
    },
  },
];
