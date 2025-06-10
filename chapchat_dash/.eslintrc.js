module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: [
    "plugin:vue/vue3-essential",
    "eslint:recommended",
    "plugin:prettier/recommended",
  ],
  parserOptions: {
    parser: "@babel/eslint-parser",
    requireConfigFile: false,
    babelOptions: {
      // <--- New section to explicitly point to your babel.config.js
      configFile: "./babel.config.js", // Path relative to your .eslintrc.js
    },
  },
  plugins: ["vue", "prettier"],

  rules: {
    quotes: "off",

    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off",
  },

  globals: {
    defineProps: "readonly",
    defineEmits: "readonly",
    defineExpose: "readonly",
    withDefaults: "readonly",
  },
};
