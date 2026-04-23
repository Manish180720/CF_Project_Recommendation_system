STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,.stDeployButton{display:none!important;}

/* ── IMDB COLORS ──
   Background:  #1a1a1a / #121212
   Surface:     #2c2c2c
   Yellow:      #F5C518
   Text:        #ffffff / #a0a0a0
*/

.stApp{background:#121212!important;}
.block-container{padding:0!important;max-width:100%!important;}

/* ── TOPBAR ── */
.topbar{position:fixed;top:0;left:0;right:0;z-index:1000;
  background:#1f1f1f;border-bottom:3px solid #F5C518;
  padding:.7rem 2rem;display:flex;align-items:center;justify-content:space-between;}
.topbar-logo{font-size:1.4rem;font-weight:900;color:#000;
  background:#F5C518;padding:.2rem .7rem;border-radius:4px;letter-spacing:-1px;}
.topbar-nav{display:flex;gap:1.8rem;align-items:center;}
.topbar-nav a{color:#fff;font-size:.88rem;font-weight:500;text-decoration:none;transition:color .15s;}
.topbar-nav a:hover{color:#F5C518;}
.topbar-right{color:#a0a0a0;font-size:.85rem;}

/* ── PUSH BELOW FIXED NAV ── */
.main-wrap{padding:4.5rem 2rem 2rem;}

/* ── AUTH PAGE ── */
.auth-page-wrap{min-height:100vh;background:#121212;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:2rem;}
.imdb-badge{font-size:2.8rem;font-weight:900;color:#000;background:#F5C518;
  padding:.3rem 1rem;border-radius:6px;letter-spacing:-2px;margin-bottom:.5rem;}
.auth-sub{color:#a0a0a0;font-size:.9rem;margin-bottom:2rem;}
.auth-card{background:#1f1f1f;border:1px solid #333;border-radius:8px;
  padding:2.5rem 2rem;width:100%;max-width:400px;}
.auth-title{font-size:1.4rem;font-weight:700;color:#fff;margin-bottom:1.5rem;}

/* ── INPUTS ── */
.stTextInput label{color:#a0a0a0!important;font-size:.78rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:.8px!important;}
.stTextInput>div>div>input{background:#2c2c2c!important;color:#fff!important;
  border:1px solid #404040!important;border-radius:4px!important;padding:.8rem!important;font-size:.95rem!important;transition:border-color .2s!important;}
.stTextInput>div>div>input:focus{border-color:#F5C518!important;outline:none!important;box-shadow:0 0 0 2px rgba(245,197,24,.2)!important;}

/* ── PRIMARY BUTTON ── */
.stButton>button{background:#F5C518!important;color:#000!important;
  font-weight:800!important;font-size:.9rem!important;border:none!important;
  border-radius:4px!important;padding:.75rem 1.5rem!important;width:100%!important;
  letter-spacing:.3px!important;transition:background .15s!important;}
.stButton>button:hover{background:#e6b800!important;box-shadow:0 2px 12px rgba(245,197,24,.4)!important;}

/* ── SECONDARY BUTTON ── */
.sec-btn .stButton>button{background:transparent!important;color:#F5C518!important;
  border:1px solid #F5C518!important;font-weight:600!important;font-size:.85rem!important;
  box-shadow:none!important;}
.sec-btn .stButton>button:hover{background:rgba(245,197,24,.1)!important;}

/* ── IMDB MOVIE CARD ── */
.imdb-card{display:flex;background:#1f1f1f;border:1px solid #2c2c2c;border-radius:6px;
  overflow:hidden;margin-bottom:10px;transition:border-color .2s,box-shadow .2s;cursor:pointer;}
.imdb-card:hover{border-color:#F5C518;box-shadow:0 0 0 1px #F5C518;}
.imdb-card-poster{min-width:80px;width:80px;height:110px;display:flex;align-items:center;
  justify-content:center;font-size:2.2rem;flex-shrink:0;}
.imdb-card-body{padding:.7rem .8rem;flex:1;min-width:0;}
.imdb-card-rank{font-size:.7rem;color:#a0a0a0;font-weight:600;text-transform:uppercase;letter-spacing:.5px;}
.imdb-card-title{font-size:.95rem;font-weight:700;color:#fff;line-height:1.3;margin:.1rem 0 .3rem;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.imdb-star{color:#F5C518;font-size:.85rem;font-weight:700;}
.imdb-card-meta{color:#a0a0a0;font-size:.75rem;margin-top:.2rem;}
.imdb-card-genres{display:flex;gap:4px;flex-wrap:wrap;margin-top:.3rem;}
.imdb-genre-chip{font-size:.65rem;color:#a0a0a0;border:1px solid #404040;border-radius:12px;padding:1px 7px;}
.imdb-card-badge{display:inline-block;background:#F5C518;color:#000;font-size:.7rem;
  font-weight:800;border-radius:3px;padding:2px 7px;margin-top:.4rem;}

/* ── GRID (for top rated, popular) ── */
.imdb-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px;margin-top:1rem;}
.imdb-grid-card{background:#1f1f1f;border:1px solid #2c2c2c;border-radius:6px;overflow:hidden;transition:border-color .2s;}
.imdb-grid-card:hover{border-color:#F5C518;}
.imdb-grid-poster{height:100px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;}
.imdb-grid-body{padding:.6rem;}
.imdb-grid-title{font-size:.78rem;font-weight:700;color:#fff;line-height:1.25;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.imdb-grid-rating{color:#F5C518;font-size:.75rem;font-weight:700;margin-top:.2rem;}
.imdb-grid-meta{color:#a0a0a0;font-size:.68rem;margin-top:.1rem;}

/* ── SECTION HEADERS ── */
.sec-hdr{font-size:1.3rem;font-weight:800;color:#fff;margin:2rem 0 .2rem;
  display:flex;align-items:center;gap:.5rem;}
.sec-hdr::after{content:'';flex:1;height:2px;background:linear-gradient(90deg,#F5C518,transparent);margin-left:.8rem;}
.sec-desc{color:#a0a0a0;font-size:.83rem;margin-bottom:.8rem;}

/* ── SELECTBOX ── */
.stSelectbox label{color:#a0a0a0!important;font-size:.78rem!important;text-transform:uppercase!important;letter-spacing:.8px!important;font-weight:600!important;}
.stSelectbox>div>div{background:#2c2c2c!important;border:1px solid #404040!important;border-radius:4px!important;color:#fff!important;}
.stSelectbox>div>div>div{color:#fff!important;}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{background:#1f1f1f!important;border-bottom:2px solid #2c2c2c!important;padding:0 1rem!important;}
.stTabs [data-baseweb="tab"]{color:#a0a0a0!important;font-weight:600!important;font-size:.88rem!important;padding:.8rem 1.2rem!important;}
.stTabs [aria-selected="true"]{color:#F5C518!important;border-bottom:2px solid #F5C518!important;}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"]{background:#1a1a1a!important;border-right:1px solid #2c2c2c!important;}
section[data-testid="stSidebar"] *{color:#fff!important;}
section[data-testid="stSidebar"] .stButton>button{background:#2c2c2c!important;color:#F5C518!important;border:1px solid #404040!important;box-shadow:none!important;font-size:.85rem!important;}

/* ── METRICS ── */
.stMetric{background:#1f1f1f!important;border:1px solid #2c2c2c!important;border-radius:6px!important;padding:.8rem!important;}
.stMetric label{color:#a0a0a0!important;font-size:.75rem!important;}
.stMetric [data-testid="stMetricValue"]{color:#F5C518!important;font-size:1.4rem!important;font-weight:800!important;}

/* ── DATAFRAME ── */
.stDataFrame{border-radius:6px!important;border:1px solid #2c2c2c!important;}
iframe{background:#1f1f1f!important;}

/* ── STATUS ── */
.stSpinner>div{border-top-color:#F5C518!important;}
.stAlert{background:#1f1f1f!important;border:1px solid #2c2c2c!important;color:#fff!important;border-radius:6px!important;}

/* ── DIVIDER ── */
hr{border-color:#2c2c2c!important;}

/* ── RADIO ── */
.stRadio label{color:#fff!important;}

/* ── OTP BOX ── */
.otp-box{background:rgba(245,197,24,.08);border:1px solid rgba(245,197,24,.3);
  border-radius:6px;padding:1rem;margin-bottom:1rem;color:#fff;font-size:.88rem;}
</style>
"""
