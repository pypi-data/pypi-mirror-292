const _import = require('eslint-plugin-import');
const node = require('eslint-plugin-node');
const promise = require('eslint-plugin-promise');
const standard = require('eslint-plugin-standard');
const cypress = require('eslint-plugin-cypress');
const chaiFriendly = require('eslint-plugin-chai-friendly');

const {
  fixupPluginRules
} = require('@eslint/compat');

const globals = require('globals');
const babelParser = require('@babel/eslint-parser');

module.exports = [
  {
    ignores: ['assets/src/thirdparty/**/*.js']
  },
  {
    plugins: {
      import: fixupPluginRules(_import),
      node,
      promise,
      standard,
      cypress,
      'chai-friendly': chaiFriendly
    },

    languageOptions: {
      globals: {
        ...globals.node,
        ...cypress.environments.globals.globals,
        document: false,
        navigator: false,
        window: false,
        $: false,
        jQuery: false,
        history: false,
        localStorage: false,
        sessionStorage: false,
        Urls: false,
        hljs: false,
        Waypoint: false,
        swh: false,
        fetch: false,
        __STATIC__: false,
        Image: false,
        nb: false,
        MathJax: false
      },

      parser: babelParser,
      ecmaVersion: 2017,
      sourceType: 'module',

      parserOptions: {
        ecmaFeatures: {
          experimentalObjectRestSpread: true,
          jsx: true
        },

        allowImportExportEverywhere: true,
        requireConfigFile: false
      }
    },

    rules: {
      'accessor-pairs': 'error',

      'arrow-spacing': ['error', {
        before: true,
        after: true
      }],

      'block-spacing': ['error', 'always'],

      'brace-style': ['error', '1tbs', {
        allowSingleLine: true
      }],

      camelcase: ['error', {
        properties: 'never'
      }],

      'comma-dangle': ['error', {
        arrays: 'never',
        objects: 'never',
        imports: 'never',
        exports: 'never',
        functions: 'never'
      }],

      'comma-spacing': ['error', {
        before: false,
        after: true
      }],

      'comma-style': ['error', 'last'],
      'constructor-super': 'error',
      curly: ['error', 'multi-line'],
      'dot-location': ['error', 'property'],
      'eol-last': 'error',

      eqeqeq: ['error', 'always', {
        null: 'ignore'
      }],

      'func-call-spacing': ['error', 'never'],

      'generator-star-spacing': ['error', {
        before: true,
        after: true
      }],

      'handle-callback-err': ['error', '^(err|error)$'],

      indent: ['error', 2, {
        SwitchCase: 1,
        VariableDeclarator: 1,
        outerIIFEBody: 1,
        MemberExpression: 'off',

        FunctionDeclaration: {
          parameters: 'first',
          body: 1
        },

        FunctionExpression: {
          parameters: 'first',
          body: 1
        },

        CallExpression: {
          arguments: 'first'
        },

        ArrayExpression: 'first',
        ObjectExpression: 'first',
        ImportDeclaration: 'first',
        flatTernaryExpressions: false,
        ignoreComments: false
      }],

      'key-spacing': ['error', {
        beforeColon: false,
        afterColon: true
      }],

      'keyword-spacing': ['error', {
        before: true,
        after: true
      }],

      'new-cap': ['error', {
        newIsCap: true,
        capIsNew: false
      }],

      'new-parens': 'error',
      'no-array-constructor': 'error',
      'no-caller': 'error',
      'no-class-assign': 'error',
      'no-compare-neg-zero': 'error',
      'no-cond-assign': 'error',
      'no-const-assign': 'error',

      'no-constant-condition': ['error', {
        checkLoops: false
      }],

      'no-control-regex': 'error',
      'no-debugger': 'error',
      'no-delete-var': 'error',
      'no-dupe-args': 'error',
      'no-dupe-class-members': 'error',
      'no-dupe-keys': 'error',
      'no-duplicate-case': 'error',
      'no-empty-character-class': 'error',
      'no-empty-pattern': 'error',
      'no-eval': 'error',
      'no-ex-assign': 'error',
      'no-extend-native': 'error',
      'no-extra-bind': 'error',
      'no-extra-boolean-cast': 'error',
      'no-extra-parens': ['error', 'functions'],
      'no-fallthrough': 'error',
      'no-floating-decimal': 'error',
      'no-func-assign': 'error',
      'no-global-assign': 'error',
      'no-implied-eval': 'error',
      'no-inner-declarations': ['error', 'functions'],
      'no-invalid-regexp': 'error',
      'no-irregular-whitespace': 'error',
      'no-iterator': 'error',
      'no-label-var': 'error',

      'no-labels': ['error', {
        allowLoop: false,
        allowSwitch: false
      }],

      'no-lone-blocks': 'error',

      'no-mixed-operators': ['error', {
        groups: [
          ['==', '!=', '===', '!==', '>', '>=', '<', '<='],
          ['&&', '||'],
          ['in', 'instanceof']
        ],

        allowSamePrecedence: true
      }],

      'no-mixed-spaces-and-tabs': 'error',
      'no-multi-spaces': 'error',
      'no-multi-str': 'error',

      'no-multiple-empty-lines': ['error', {
        max: 1,
        maxEOF: 0
      }],

      'no-negated-in-lhs': 'error',
      'no-new': 0,
      'no-new-func': 'error',
      'no-new-object': 'error',
      'no-new-require': 'error',
      'no-new-symbol': 'error',
      'no-new-wrappers': 'error',
      'no-obj-calls': 'error',
      'no-octal': 'error',
      'no-octal-escape': 'error',
      'no-path-concat': 'error',
      'no-proto': 'error',
      'no-redeclare': 'error',
      'no-regex-spaces': 'error',
      'no-return-assign': ['error', 'except-parens'],
      'no-return-await': 'error',
      'no-self-assign': 'error',
      'no-self-compare': 'error',
      'no-sequences': 'error',
      'no-shadow-restricted-names': 'error',
      'no-sparse-arrays': 'error',
      'no-tabs': 'error',
      'no-template-curly-in-string': 'error',
      'no-this-before-super': 'error',
      'no-throw-literal': 'error',
      'no-trailing-spaces': 'error',
      'no-undef': 'error',
      'no-undef-init': 'error',
      'no-unexpected-multiline': 'error',
      'no-unmodified-loop-condition': 'error',

      'no-unneeded-ternary': ['error', {
        defaultAssignment: false
      }],

      'no-unreachable': 'error',
      'no-unsafe-finally': 'error',
      'no-unsafe-negation': 'error',
      'no-unused-expressions': 0,

      'no-unused-vars': ['error', {
        vars: 'all',
        args: 'none',
        ignoreRestSiblings: true,
        caughtErrors: 'none'
      }],

      'no-use-before-define': ['error', {
        functions: false,
        classes: false,
        variables: false
      }],

      'no-useless-call': 'error',
      'no-useless-computed-key': 'error',
      'no-useless-constructor': 'error',
      'no-useless-escape': 'error',
      'no-useless-rename': 'error',
      'no-useless-return': 'error',
      'no-whitespace-before-property': 'error',
      'no-with': 'error',

      'object-property-newline': ['error', {
        allowMultiplePropertiesPerLine: true
      }],

      'one-var': ['error', {
        initialized: 'never'
      }],

      'operator-linebreak': ['error', 'after', {
        overrides: {
          '?': 'before',
          ':': 'before'
        }
      }],

      'padded-blocks': ['off', {
        blocks: 'never',
        switches: 'never',
        classes: 'never'
      }],

      'prefer-promise-reject-errors': 'error',

      'prefer-const': ['error', {
        destructuring: 'any',
        ignoreReadBeforeAssign: false
      }],

      quotes: ['error', 'single', {
        avoidEscape: true,
        allowTemplateLiterals: true
      }],

      'rest-spread-spacing': ['error', 'never'],
      semi: ['error', 'always'],

      'semi-spacing': ['error', {
        before: false,
        after: true
      }],

      'space-before-blocks': ['error', 'always'],
      'space-before-function-paren': ['error', 'never'],
      'space-in-parens': ['error', 'never'],
      'space-infix-ops': 'error',

      'space-unary-ops': ['error', {
        words: true,
        nonwords: false
      }],

      'spaced-comment': ['error', 'always', {
        line: {
          markers: ['*package', '!', '/', ',', '=']
        },

        block: {
          balanced: true,
          markers: ['*package', '!', ',', ':', '::', 'flow-include'],
          exceptions: ['*']
        }
      }],

      'symbol-description': 'error',
      'template-curly-spacing': ['error', 'never'],
      'template-tag-spacing': ['error', 'never'],
      'unicode-bom': ['error', 'never'],
      'use-isnan': 'error',

      'valid-typeof': ['error', {
        requireStringLiterals: true
      }],

      'wrap-iife': ['error', 'any', {
        functionPrototypeMethods: true
      }],

      'yield-star-spacing': ['error', 'both'],
      yoda: ['error', 'never'],
      'import/export': 'off',
      'import/first': 'error',
      'import/no-duplicates': 'error',
      'import/no-webpack-loader-syntax': 'off',
      'node/process-exit-as-throw': 'error',
      'promise/param-names': 'error',
      'standard/no-callback-literal': 'error',
      'chai-friendly/no-unused-expressions': 2,
      'object-curly-spacing': ['error', 'never']
    }
  }
];
