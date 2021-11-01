module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: ["plugin:vue/recommended", "airbnb", "prettier"],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: "module",
  },
  plugins: ["vue", "prettier", "import"],
  rules: {
    "import/extensions": [0, { "<js>": "always" }],
    quotes: [2, "double"],
    "object-shorthand": ["error", "never"]
    "func-names": ["error", "never"]
  },
};
