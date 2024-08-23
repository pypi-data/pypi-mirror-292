/*
Language: Excel formulae
Author: Victor Zhou <OiCMudkips@users.noreply.github.com>
Description: Excel formulae
Website: https://products.office.com/en-us/excel/
Category: enterprise
*/

/** @type LanguageFn */
function excel(hljs) {
  // built-in functions imported from https://web.archive.org/web/20160513042710/https://support.office.com/en-us/article/Excel-functions-alphabetical-b3944572-255d-4efb-bb96-c6d90033e188
  const BUILT_INS = [
    "ABS",
    "ACCRINT",
    "ACCRINTM",
    "ACOS",
    "ACOSH",
    "ACOT",
    "ACOTH",
    "AGGREGATE",
    "ADDRESS",
    "AMORDEGRC",
    "AMORLINC",
    "AND",
    "ARABIC",
    "AREAS",
    "ASC",
    "ASIN",
    "ASINH",
    "ATAN",
    "ATAN2",
    "ATANH",
    "AVEDEV",
    "AVERAGE",
    "AVERAGEA",
    "AVERAGEIF",
    "AVERAGEIFS",
    "BAHTTEXT",
    "BASE",
    "BESSELI",
    "BESSELJ",
    "BESSELK",
    "BESSELY",
    "BETADIST",
    "BETA.DIST",
    "BETAINV",
    "BETA.INV",
    "BIN2DEC",
    "BIN2HEX",
    "BIN2OCT",
    "BINOMDIST",
    "BINOM.DIST",
    "BINOM.DIST.RANGE",
    "BINOM.INV",
    "BITAND",
    "BITLSHIFT",
    "BITOR",
    "BITRSHIFT",
    "BITXOR",
    "CALL",
    "CEILING",
    "CEILING.MATH",
    "CEILING.PRECISE",
    "CELL",
    "CHAR",
    "CHIDIST",
    "CHIINV",
    "CHITEST",
    "CHISQ.DIST",
    "CHISQ.DIST.RT",
    "CHISQ.INV",
    "CHISQ.INV.RT",
    "CHISQ.TEST",
    "CHOOSE",
    "CLEAN",
    "CODE",
    "COLUMN",
    "COLUMNS",
    "COMBIN",
    "COMBINA",
    "COMPLEX",
    "CONCAT",
    "CONCATENATE",
    "CONFIDENCE",
    "CONFIDENCE.NORM",
    "CONFIDENCE.T",
    "CONVERT",
    "CORREL",
    "COS",
    "COSH",
    "COT",
    "COTH",
    "COUNT",
    "COUNTA",
    "COUNTBLANK",
    "COUNTIF",
    "COUNTIFS",
    "COUPDAYBS",
    "COUPDAYS",
    "COUPDAYSNC",
    "COUPNCD",
    "COUPNUM",
    "COUPPCD",
    "COVAR",
    "COVARIANCE.P",
    "COVARIANCE.S",
    "CRITBINOM",
    "CSC",
    "CSCH",
    "CUBEKPIMEMBER",
    "CUBEMEMBER",
    "CUBEMEMBERPROPERTY",
    "CUBERANKEDMEMBER",
    "CUBESET",
    "CUBESETCOUNT",
    "CUBEVALUE",
    "CUMIPMT",
    "CUMPRINC",
    "DATE",
    "DATEDIF",
    "DATEVALUE",
    "DAVERAGE",
    "DAY",
    "DAYS",
    "DAYS360",
    "DB",
    "DBCS",
    "DCOUNT",
    "DCOUNTA",
    "DDB",
    "DEC2BIN",
    "DEC2HEX",
    "DEC2OCT",
    "DECIMAL",
    "DEGREES",
    "DELTA",
    "DEVSQ",
    "DGET",
    "DISC",
    "DMAX",
    "DMIN",
    "DOLLAR",
    "DOLLARDE",
    "DOLLARFR",
    "DPRODUCT",
    "DSTDEV",
    "DSTDEVP",
    "DSUM",
    "DURATION",
    "DVAR",
    "DVARP",
    "EDATE",
    "EFFECT",
    "ENCODEURL",
    "EOMONTH",
    "ERF",
    "ERF.PRECISE",
    "ERFC",
    "ERFC.PRECISE",
    "ERROR.TYPE",
    "EUROCONVERT",
    "EVEN",
    "EXACT",
    "EXP",
    "EXPON.DIST",
    "EXPONDIST",
    "FACT",
    "FACTDOUBLE",
    "FALSE|0",
    "F.DIST",
    "FDIST",
    "F.DIST.RT",
    "FILTERXML",
    "FIND",
    "FINDB",
    "F.INV",
    "F.INV.RT",
    "FINV",
    "FISHER",
    "FISHERINV",
    "FIXED",
    "FLOOR",
    "FLOOR.MATH",
    "FLOOR.PRECISE",
    "FORECAST",
    "FORECAST.ETS",
    "FORECAST.ETS.CONFINT",
    "FORECAST.ETS.SEASONALITY",
    "FORECAST.ETS.STAT",
    "FORECAST.LINEAR",
    "FORMULATEXT",
    "FREQUENCY",
    "F.TEST",
    "FTEST",
    "FV",
    "FVSCHEDULE",
    "GAMMA",
    "GAMMA.DIST",
    "GAMMADIST",
    "GAMMA.INV",
    "GAMMAINV",
    "GAMMALN",
    "GAMMALN.PRECISE",
    "GAUSS",
    "GCD",
    "GEOMEAN",
    "GESTEP",
    "GETPIVOTDATA",
    "GROWTH",
    "HARMEAN",
    "HEX2BIN",
    "HEX2DEC",
    "HEX2OCT",
    "HLOOKUP",
    "HOUR",
    "HYPERLINK",
    "HYPGEOM.DIST",
    "HYPGEOMDIST",
    "IF",
    "IFERROR",
    "IFNA",
    "IFS",
    "IMABS",
    "IMAGINARY",
    "IMARGUMENT",
    "IMCONJUGATE",
    "IMCOS",
    "IMCOSH",
    "IMCOT",
    "IMCSC",
    "IMCSCH",
    "IMDIV",
    "IMEXP",
    "IMLN",
    "IMLOG10",
    "IMLOG2",
    "IMPOWER",
    "IMPRODUCT",
    "IMREAL",
    "IMSEC",
    "IMSECH",
    "IMSIN",
    "IMSINH",
    "IMSQRT",
    "IMSUB",
    "IMSUM",
    "IMTAN",
    "INDEX",
    "INDIRECT",
    "INFO",
    "INT",
    "INTERCEPT",
    "INTRATE",
    "IPMT",
    "IRR",
    "ISBLANK",
    "ISERR",
    "ISERROR",
    "ISEVEN",
    "ISFORMULA",
    "ISLOGICAL",
    "ISNA",
    "ISNONTEXT",
    "ISNUMBER",
    "ISODD",
    "ISREF",
    "ISTEXT",
    "ISO.CEILING",
    "ISOWEEKNUM",
    "ISPMT",
    "JIS",
    "KURT",
    "LARGE",
    "LCM",
    "LEFT",
    "LEFTB",
    "LEN",
    "LENB",
    "LINEST",
    "LN",
    "LOG",
    "LOG10",
    "LOGEST",
    "LOGINV",
    "LOGNORM.DIST",
    "LOGNORMDIST",
    "LOGNORM.INV",
    "LOOKUP",
    "LOWER",
    "MATCH",
    "MAX",
    "MAXA",
    "MAXIFS",
    "MDETERM",
    "MDURATION",
    "MEDIAN",
    "MID",
    "MIDBs",
    "MIN",
    "MINIFS",
    "MINA",
    "MINUTE",
    "MINVERSE",
    "MIRR",
    "MMULT",
    "MOD",
    "MODE",
    "MODE.MULT",
    "MODE.SNGL",
    "MONTH",
    "MROUND",
    "MULTINOMIAL",
    "MUNIT",
    "N",
    "NA",
    "NEGBINOM.DIST",
    "NEGBINOMDIST",
    "NETWORKDAYS",
    "NETWORKDAYS.INTL",
    "NOMINAL",
    "NORM.DIST",
    "NORMDIST",
    "NORMINV",
    "NORM.INV",
    "NORM.S.DIST",
    "NORMSDIST",
    "NORM.S.INV",
    "NORMSINV",
    "NOT",
    "NOW",
    "NPER",
    "NPV",
    "NUMBERVALUE",
    "OCT2BIN",
    "OCT2DEC",
    "OCT2HEX",
    "ODD",
    "ODDFPRICE",
    "ODDFYIELD",
    "ODDLPRICE",
    "ODDLYIELD",
    "OFFSET",
    "OR",
    "PDURATION",
    "PEARSON",
    "PERCENTILE.EXC",
    "PERCENTILE.INC",
    "PERCENTILE",
    "PERCENTRANK.EXC",
    "PERCENTRANK.INC",
    "PERCENTRANK",
    "PERMUT",
    "PERMUTATIONA",
    "PHI",
    "PHONETIC",
    "PI",
    "PMT",
    "POISSON.DIST",
    "POISSON",
    "POWER",
    "PPMT",
    "PRICE",
    "PRICEDISC",
    "PRICEMAT",
    "PROB",
    "PRODUCT",
    "PROPER",
    "PV",
    "QUARTILE",
    "QUARTILE.EXC",
    "QUARTILE.INC",
    "QUOTIENT",
    "RADIANS",
    "RAND",
    "RANDBETWEEN",
    "RANK.AVG",
    "RANK.EQ",
    "RANK",
    "RATE",
    "RECEIVED",
    "REGISTER.ID",
    "REPLACE",
    "REPLACEB",
    "REPT",
    "RIGHT",
    "RIGHTB",
    "ROMAN",
    "ROUND",
    "ROUNDDOWN",
    "ROUNDUP",
    "ROW",
    "ROWS",
    "RRI",
    "RSQ",
    "RTD",
    "SEARCH",
    "SEARCHB",
    "SEC",
    "SECH",
    "SECOND",
    "SERIESSUM",
    "SHEET",
    "SHEETS",
    "SIGN",
    "SIN",
    "SINH",
    "SKEW",
    "SKEW.P",
    "SLN",
    "SLOPE",
    "SMALL",
    "SQL.REQUEST",
    "SQRT",
    "SQRTPI",
    "STANDARDIZE",
    "STDEV",
    "STDEV.P",
    "STDEV.S",
    "STDEVA",
    "STDEVP",
    "STDEVPA",
    "STEYX",
    "SUBSTITUTE",
    "SUBTOTAL",
    "SUM",
    "SUMIF",
    "SUMIFS",
    "SUMPRODUCT",
    "SUMSQ",
    "SUMX2MY2",
    "SUMX2PY2",
    "SUMXMY2",
    "SWITCH",
    "SYD",
    "T",
    "TAN",
    "TANH",
    "TBILLEQ",
    "TBILLPRICE",
    "TBILLYIELD",
    "T.DIST",
    "T.DIST.2T",
    "T.DIST.RT",
    "TDIST",
    "TEXT",
    "TEXTJOIN",
    "TIME",
    "TIMEVALUE",
    "T.INV",
    "T.INV.2T",
    "TINV",
    "TODAY",
    "TRANSPOSE",
    "TREND",
    "TRIM",
    "TRIMMEAN",
    "TRUE|0",
    "TRUNC",
    "T.TEST",
    "TTEST",
    "TYPE",
    "UNICHAR",
    "UNICODE",
    "UPPER",
    "VALUE",
    "VAR",
    "VAR.P",
    "VAR.S",
    "VARA",
    "VARP",
    "VARPA",
    "VDB",
    "VLOOKUP",
    "WEBSERVICE",
    "WEEKDAY",
    "WEEKNUM",
    "WEIBULL",
    "WEIBULL.DIST",
    "WORKDAY",
    "WORKDAY.INTL",
    "XIRR",
    "XNPV",
    "XOR",
    "YEAR",
    "YEARFRAC",
    "YIELD",
    "YIELDDISC",
    "YIELDMAT",
    "Z.TEST",
    "ZTEST"
  ];
  return {
    name: 'Excel formulae',
    aliases: [
      'xlsx',
      'xls'
    ],
    case_insensitive: true,
    keywords: {
      $pattern: /[a-zA-Z][\w\.]*/,
      built_in: BUILT_INS
    },
    contains: [
      {
        /* matches a beginning equal sign found in Excel formula examples */
        begin: /^=/,
        end: /[^=]/,
        returnEnd: true,
        illegal: /=/, /* only allow single equal sign at front of line */
        relevance: 10
      },
      /* technically, there can be more than 2 letters in column names, but this prevents conflict with some keywords */
      {
        /* matches a reference to a single cell */
        className: 'symbol',
        begin: /\b[A-Z]{1,2}\d+\b/,
        end: /[^\d]/,
        excludeEnd: true,
        relevance: 0
      },
      {
        /* matches a reference to a range of cells */
        className: 'symbol',
        begin: /[A-Z]{0,2}\d*:[A-Z]{0,2}\d*/,
        relevance: 0
      },
      hljs.BACKSLASH_ESCAPE,
      hljs.QUOTE_STRING_MODE,
      {
        className: 'number',
        begin: hljs.NUMBER_RE + '(%)?',
        relevance: 0
      },
      /* Excel formula comments are done by putting the comment in a function call to N() */
      hljs.COMMENT(/\bN\(/, /\)/,
        {
          excludeBegin: true,
          excludeEnd: true,
          illegal: /\n/
        })
    ]
  };
}

module.exports = excel;
