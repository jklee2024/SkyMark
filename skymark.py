"""
SkyMark v2.0
MSFS 2024 VFR 파일럿을 위한 실시간 오버레이

설치: pip install SimConnect
실행: py skymark.py
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
import math, threading, time, json, os, webbrowser, urllib.request, csv

try:
    from SimConnect import SimConnect, AircraftRequests
    SC_OK = True
except ImportError:
    SC_OK = False

# ── 경로 ──────────────────────────────────────────────────────────────
BASE     = os.path.dirname(os.path.abspath(__file__))
POI_FILE = os.path.join(BASE, "skymark_poi.json")
CFG_FILE = os.path.join(BASE, "skymark_config.json")
APT_FILE = os.path.join(BASE, "airports.csv")

# ── 색상 팔레트 ───────────────────────────────────────────────────────
BG      = "#1a2535"   # 메인 배경 (더 밝게)
BG2     = "#243447"   # 패널 배경 (더 밝게)
BG3     = "#2d3f55"   # 카드 배경 (더 밝게)
BORDER  = "#3d5a7a"   # 테두리 (더 밝게)
WHITE   = "#ffffff"
DIM     = "#8899aa"
ACCENT  = "#4da6ff"   # 파란 강조
GREEN   = "#00cc66"   # 초록
ORANGE  = "#ff8c00"   # 주황
RED     = "#ff4444"   # 빨강
YELLOW  = "#ffd700"   # 노랑
PURPLE  = "#bb88ff"   # 보라

# ── 폰트 ──────────────────────────────────────────────────────────────
FH  = ("맑은 고딕", 11, "bold")    # 헤더
FB  = ("맑은 고딕", 10, "bold")    # 버튼
FN  = ("맑은 고딕", 10)            # 일반
FS  = ("맑은 고딕", 9)             # 작은
FV  = ("맑은 고딕", 18, "bold")    # 큰 값
FM  = ("맑은 고딕", 13, "bold")    # 중간 값
FC  = ("맑은 고딕", 11, "bold")    # 컴팩트
FXS = ("맑은 고딕", 8)             # 아주 작은

# ── 언어팩 ────────────────────────────────────────────────────────────
LANG = {
    "ko": {
        "title": "SkyMark",
        "connected": "연결됨 (MSFS 2024)",
        "waiting": "대기 중...",
        "hdg_up": "기수 기준",
        "nth_up": "진북 기준",
        "lang_btn": "English",
        "wind_panel": "바람 정보",
        "data_panel": "비행 데이터",
        "nav_panel": "항법 정보",
        "apt_panel": "가까운 공항",
        "poi_panel": "POI 목록",
        "settings_panel": "설정",
        "summary_panel": "요약 정보",
        "wind_dir": "풍향",
        "wind_spd": "풍속",
        "headwind": "정면풍",
        "crosswind": "크로스윈드",
        "oat": "기온 OAT",
        "density": "밀도고도",
        "alt_msl": "고도 MSL",
        "alt_agl": "고도 AGL",
        "ias": "IAS",
        "tas": "TAS",
        "vsi": "VSI",
        "qnh": "QNH",
        "rpm": "RPM",
        "fuel": "연료 잔량",
        "home": "출발지 (Home)",
        "dest": "목적지 (Destination)",
        "position": "현재 위치",
        "bearing": "방향",
        "distance": "거리",
        "lat": "위도",
        "lon": "경도",
        "alt": "고도",
        "apt_name": "공항명",
        "apt_dir": "방향",
        "apt_dist": "거리",
        "set_home": "출발지 설정",
        "set_dest": "목적지 설정",
        "save_poi": "+ 새로 저장",
        "no_poi": "저장된 POI 없음",
        "earth": "Google Earth 열기",
        "delete": "삭제",
        "edit": "편집",
        "sort_recent": "최신순",
        "sort_near": "가까운순",
        "poi_input": "POI 이름 입력...",
        "save_btn": "현재 위치 저장",
        "all_poi": "전체 POI 보기",
        "display": "표시 설정",
        "theme": "테마 색상",
        "opacity": "투명도",
        "fontsize": "글자 크기",
        "general": "일반 설정",
        "language": "언어",
        "temp_unit": "온도 단위",
        "spd_unit": "속도 단위",
        "alt_unit": "고도 단위",
        "misc": "기타",
        "auto_conn": "자동 연결",
        "always_top": "창 항상 위에 표시",
        "start_mini": "시작 시 최소화",
        "right": "우",
        "left": "좌",
        "front": "정면",
        "rear": "후방",
        "headwind_lbl": "정면풍",
        "tailwind_lbl": "뒷바람",
        "beaufort": "풍속 단계 (Beaufort)",
        "collapse": "접기",
        "expand": "펼치기",
        "nm": "NM",
        "fwd": "앞", "aft": "뒤", "lft": "좌", "rgt": "우",
        "enter_name": "이름을 입력하세요",
        "del_confirm": "삭제하시겠습니까?",
        "apt_download_fail": "공항 데이터 다운로드 실패\n인터넷 연결을 확인하세요.",
        "vr_notice": "※ VR 모드에서는 표시되지 않을 수 있습니다",
        "wind_note": "※ 풍향은 바람이 불어오는 방향(FROM)입니다",
    },
    "en": {
        "title": "SkyMark",
        "connected": "Connected (MSFS 2024)",
        "waiting": "Waiting...",
        "hdg_up": "HDG UP",
        "nth_up": "North UP",
        "lang_btn": "한국어",
        "wind_panel": "Wind Info",
        "data_panel": "Flight Data",
        "nav_panel": "Navigation",
        "apt_panel": "Nearest Airports",
        "poi_panel": "Waypoints",
        "settings_panel": "Settings",
        "summary_panel": "Summary",
        "wind_dir": "Wind Dir",
        "wind_spd": "Wind Spd",
        "headwind": "Headwind",
        "crosswind": "Crosswind",
        "oat": "OAT",
        "density": "Density Alt",
        "alt_msl": "Alt MSL",
        "alt_agl": "Alt AGL",
        "ias": "IAS",
        "tas": "TAS",
        "vsi": "VSI",
        "qnh": "QNH",
        "rpm": "RPM",
        "fuel": "Fuel",
        "home": "Home",
        "dest": "Destination",
        "position": "Current Position",
        "bearing": "Bearing",
        "distance": "Distance",
        "lat": "Lat",
        "lon": "Lon",
        "alt": "Alt",
        "apt_name": "Airport",
        "apt_dir": "Bearing",
        "apt_dist": "Dist",
        "set_home": "Set Home",
        "set_dest": "Set Dest",
        "save_poi": "+ Save Here",
        "no_poi": "No waypoints saved",
        "earth": "Google Earth",
        "delete": "Del",
        "edit": "Edit",
        "sort_recent": "Recent",
        "sort_near": "Nearest",
        "poi_input": "Enter POI name...",
        "save_btn": "Save Current Position",
        "all_poi": "View All POI",
        "display": "Display",
        "theme": "Theme Color",
        "opacity": "Opacity",
        "fontsize": "Font Size",
        "general": "General",
        "language": "Language",
        "temp_unit": "Temperature",
        "spd_unit": "Speed",
        "alt_unit": "Altitude",
        "misc": "Other",
        "auto_conn": "Auto Connect",
        "always_top": "Always on Top",
        "start_mini": "Start Minimized",
        "right": "R",
        "left": "L",
        "front": "Fwd",
        "rear": "Aft",
        "headwind_lbl": "Headwind",
        "tailwind_lbl": "Tailwind",
        "beaufort": "Beaufort Scale",
        "collapse": "Collapse",
        "expand": "Expand",
        "nm": "NM",
        "fwd": "FWD", "aft": "AFT", "lft": "L", "rgt": "R",
        "enter_name": "Enter name",
        "del_confirm": "Delete this waypoint?",
        "apt_download_fail": "Airport data download failed.\nCheck your internet connection.",
        "vr_notice": "※ Not supported in VR mode",
        "wind_note": "※ Wind direction = direction wind is coming FROM",
    }
}

# ── 유틸 ──────────────────────────────────────────────────────────────
def haversine(la1, lo1, la2, lo2):
    R = 3440.065
    la1,lo1,la2,lo2 = map(math.radians,[la1,lo1,la2,lo2])
    dla=la2-la1; dlo=lo2-lo1
    a = math.sin(dla/2)**2 + math.cos(la1)*math.cos(la2)*math.sin(dlo/2)**2
    d = R*2*math.asin(math.sqrt(max(0,min(1,a))))
    x = math.sin(lo2-lo1)*math.cos(la2)
    y = math.cos(la1)*math.sin(la2)-math.sin(la1)*math.cos(la2)*math.cos(lo2-lo1)
    b = math.degrees(math.atan2(x,y))%360
    return d,b

def rel_brg(ab, hdg): return (ab-hdg+360)%360

def brg_txt(rel, L):
    if rel>180: rel-=360
    if   abs(rel)<=15:  return L["front"]
    elif abs(rel)>=165: return L["rear"]
    elif rel>0:         return f"{L['right']} {rel:.0f}°"
    else:               return f"{L['left']} {abs(rel):.0f}°"

def bft(kt):
    stages = [(1,"Calm"),(4,"실바람"),(7,"남실바람"),(11,"산들바람"),
              (17,"건들바람"),(22,"흔들바람"),(28,"된바람"),(34,"센바람")]
    for limit, name in stages:
        if kt < limit: return name
    return "강풍 ⚠"

def wind_color(kt):
    if kt < 15: return WHITE
    if kt < 25: return ORANGE
    return RED

def stext(c, x, y, text, font, fill, anchor="center"):
    for dx,dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
        c.create_text(x+dx,y+dy,text=text,font=font,fill="#000000",anchor=anchor)
    c.create_text(x,y,text=text,font=font,fill=fill,anchor=anchor)


class Panel(tk.Frame):
    """닫기 버튼이 있는 패널 베이스 클래스"""
    def __init__(self, parent, title, on_close, bg=BG2, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.configure(highlightbackground=BORDER, highlightthickness=1)

        # 헤더
        hdr = tk.Frame(self, bg=bg)
        hdr.pack(fill="x", padx=8, pady=(6,0))

        self.title_lbl = tk.Label(hdr, text=title, font=FH, bg=bg, fg=WHITE)
        self.title_lbl.pack(side="left")

        close_btn = tk.Label(hdr, text="×", font=("맑은 고딕",13,"bold"),
            bg=bg, fg=DIM, cursor="hand2")
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: on_close())

        # 구분선
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=8, pady=(4,0))

        # 내용 영역
        self.body = tk.Frame(self, bg=bg)
        self.body.pack(fill="both", expand=True, padx=8, pady=6)


class SkyMark:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SkyMark v2.0")
        self.root.configure(bg=BG)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.82)   # 더 투명하게
        self.root.resizable(True, True)
        self.root.geometry("1200x820+50+50")

        # 드래그
        self._dx = self._dy = 0
        self.root.bind_all("<ButtonPress-1>", self._ds)
        self.root.bind_all("<B1-Motion>",     self._dm)

        self._load_cfg()

        # 상태
        self.hdg_up   = True
        self.expanded = True

        # 비행 데이터
        self.lat=self.lon=self.wdir=self.wspd=self.hdg=0.0
        self.oat=self.da=self.msl=self.agl=0.0
        self.ias=self.tas=self.vsi=self.fl=self.fr=self.rpm=self.qnh=0.0
        self.ok = False

        self.pois = self._load_pois()
        self.home = self.cfg.get("home", None)
        self.dest = self.cfg.get("dest", None)
        self.apts = []
        self.apt_status = "loading"
        self._tick_count = 0  # 틱 카운터 (공항/POI 업데이트 주기 조절)

        # 패널 표시 상태
        self.panel_visible = {
            "wind": True, "data": True, "nav": True,
            "apt": True, "poi": True, "settings": False
        }

        threading.Thread(target=self._load_apts, daemon=True).start()
        self._build()

        self.running = True
        threading.Thread(target=self._poll, daemon=True).start()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self._tick()
        self.root.mainloop()

    # ── 설정 ─────────────────────────────────────────────────────────
    def _load_cfg(self):
        try:
            with open(CFG_FILE, encoding="utf-8") as f: self.cfg=json.load(f)
        except: self.cfg={"lang":"en"}
        self.lc = self.cfg.get("lang","en")

    def _save_cfg(self):
        self.cfg.update({"lang":self.lc,"home":self.home,"dest":self.dest})
        with open(CFG_FILE,"w",encoding="utf-8") as f:
            json.dump(self.cfg,f,ensure_ascii=False,indent=2)

    def L(self,k): return LANG[self.lc].get(k,k)

    # ── POI ──────────────────────────────────────────────────────────
    def _load_pois(self):
        try:
            with open(POI_FILE,encoding="utf-8") as f: return json.load(f)
        except: return []

    def _save_pois(self):
        with open(POI_FILE,"w",encoding="utf-8") as f:
            json.dump(self.pois,f,ensure_ascii=False,indent=2)

    # ── 공항 데이터 ──────────────────────────────────────────────────
    def _load_apts(self):
        self.apt_status = "loading"
        if not os.path.exists(APT_FILE):
            try:
                urllib.request.urlretrieve(
                    "https://davidmegginson.github.io/ourairports-data/airports.csv",
                    APT_FILE)
            except:
                self.apt_status = "fail"
                return
        try:
            apts=[]
            with open(APT_FILE,encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    if r.get("type","") in ("closed","heliport","seaplane_base"): continue
                    try:
                        apts.append({"icao":r.get("ident",""),
                            "name":r.get("name",""),
                            "lat":float(r.get("latitude_deg",0)),
                            "lon":float(r.get("longitude_deg",0))})
                    except: pass
            self.apts=apts
            self.apt_status = "ok"
        except:
            self.apt_status = "fail"

    # ── UI 빌드 ───────────────────────────────────────────────────────
    def _build(self):
        # ── 상단 바 ──────────────────────────────────────────────────
        self._build_topbar()

        # ── 컴팩트 바 (접힌 상태) ────────────────────────────────────
        self._build_compact()

        # ── 메인 패널 영역 ───────────────────────────────────────────
        self.main_frame = tk.Frame(self.root, bg=BG)
        self.main_frame.pack(fill="both", expand=True, padx=8, pady=(0,8))

        # 상단 행: 바람 | 비행데이터 | 항법
        self.row1 = tk.Frame(self.main_frame, bg=BG)
        self.row1.pack(fill="both", expand=True, pady=(0,4))

        # 하단 행: 공항 | POI
        self.row2 = tk.Frame(self.main_frame, bg=BG)
        self.row2.pack(fill="both", expand=True)

        self._build_wind_panel()
        self._build_data_panel()
        self._build_nav_panel()
        self._build_apt_panel()
        self._build_poi_panel()

    def _build_topbar(self):
        bar = tk.Frame(self.root, bg=BG2, height=44)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # 로고
        tk.Label(bar, text="✈", font=("맑은 고딕",16), bg=BG2, fg=ACCENT).pack(side="left", padx=(12,4))
        tk.Label(bar, text="SkyMark", font=("맑은 고딕",14,"bold"), bg=BG2, fg=WHITE).pack(side="left")

        # 오른쪽 버튼들
        # 닫기
        close_lbl = tk.Label(bar, text="✕", font=("맑은 고딕",13),
            bg=BG2, fg=DIM, cursor="hand2")
        close_lbl.pack(side="right", padx=(0,12))
        close_lbl.bind("<Button-1>", lambda e: self._close())

        # 최소화
        mini_lbl = tk.Label(bar, text="—", font=("맑은 고딕",13),
            bg=BG2, fg=DIM, cursor="hand2")
        mini_lbl.pack(side="right", padx=(0,6))
        mini_lbl.bind("<Button-1>", lambda e: self.root.iconify())

        # 언어
        self.lang_btn = tk.Label(bar, text=self.L("lang_btn"),
            font=FB, bg=BG3, fg=WHITE, cursor="hand2",
            padx=10, pady=2, relief="flat")
        self.lang_btn.pack(side="right", padx=(0,8))
        self.lang_btn.bind("<Button-1>", lambda e: self._toggle_lang())

        # 진북/기수 전환
        self.nth_btn = tk.Label(bar, text=f"↑ {self.L('nth_up')}",
            font=FB, bg=BG3, fg=DIM, cursor="hand2",
            padx=10, pady=2)
        self.nth_btn.pack(side="right", padx=(0,4))
        self.nth_btn.bind("<Button-1>", lambda e: self._set_mode(False))

        self.hdg_btn = tk.Label(bar, text=f"↑ {self.L('hdg_up')}",
            font=FB, bg=ACCENT, fg=WHITE, cursor="hand2",
            padx=10, pady=2)
        self.hdg_btn.pack(side="right", padx=(0,4))
        self.hdg_btn.bind("<Button-1>", lambda e: self._set_mode(True))

        # 연결 상태
        self.conn_dot = tk.Label(bar, text="●", font=("맑은 고딕",12), bg=BG2, fg=ORANGE)
        self.conn_dot.pack(side="right", padx=(0,4))
        self.conn_lbl = tk.Label(bar, text=self.L("waiting"), font=FS, bg=BG2, fg=DIM)
        self.conn_lbl.pack(side="right", padx=(0,8))

        # 구분선
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        # ── 패널 토글 버튼 바 ────────────────────────────────────────
        self._build_toggle_bar()

        # 구분선
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

    def _build_compact(self):
        """접힌 상태 요약 바"""
        self.compact_bar = tk.Frame(self.root, bg=BG2, height=36)
        # 처음엔 숨김 (펼친 상태가 기본)

        inner = tk.Frame(self.compact_bar, bg=BG2)
        inner.pack(fill="x", padx=12)

        items = [
            ("wind_sum", "✈ ---° --kt", ORANGE),
            ("oat_sum",  "🌡 --°C", WHITE),
            ("alt_sum",  "▲ ----ft", WHITE),
            ("ias_sum",  "IAS --kt", WHITE),
            ("tas_sum",  "TAS --kt", WHITE),
            ("rpm_sum",  "RPM ----", WHITE),
            ("fuel_sum", "⛽ --gal", WHITE),
            ("home_sum", "🏠 --NM", ACCENT),
            ("dest_sum", "🚩 --NM", YELLOW),
        ]
        self.sum_lbls = {}
        for key, text, color in items:
            lbl = tk.Label(inner, text=text, font=FS, bg=BG2, fg=color)
            lbl.pack(side="left", padx=(0,16))
            self.sum_lbls[key] = lbl

        expand_btn = tk.Label(inner, text="▲ 펼치기", font=FB,
            bg=BG3, fg=WHITE, cursor="hand2", padx=8)
        expand_btn.pack(side="right")
        expand_btn.bind("<Button-1>", lambda e: self._toggle_expand())

        # 투명도 슬라이더
        tk.Label(inner, text="투명도", font=FXS, bg=BG2, fg=DIM).pack(side="right", padx=(0,4))
        self.alpha_slider = tk.Scale(inner, from_=40, to=100,
            orient="horizontal", length=80, showvalue=False,
            bg=BG2, fg=DIM, troughcolor=BG3, highlightthickness=0,
            command=self._set_alpha)
        self.alpha_slider.set(92)
        self.alpha_slider.pack(side="right", padx=(0,4))

    def _build_toggle_bar(self):
        """패널 켜기/끄기 토글 버튼 바"""
        bar = tk.Frame(self.root, bg=BG2, height=32)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        collapse_btn = tk.Label(bar, text="접기 ▼", font=FB, bg=BG2, fg=DIM,
            cursor="hand2")
        collapse_btn.pack(side="right", padx=(0,12))
        collapse_btn.bind("<Button-1>", lambda e: self._toggle_expand())

        panels = [
            ("wind", self.L("wind_panel")),
            ("data", self.L("data_panel")),
            ("nav",  self.L("nav_panel")),
            ("apt",  self.L("apt_panel")),
            ("poi",  self.L("poi_panel")),
        ]
        self.toggle_btns = {}
        for key, label in panels:
            btn = tk.Label(bar, text=label, font=FS,
                bg=ACCENT if self.panel_visible[key] else BG3,
                fg=WHITE, cursor="hand2", padx=8, pady=2)
            btn.pack(side="left", padx=(8,0))
            btn.bind("<Button-1>", lambda e, k=key: self._toggle_panel(k))
            self.toggle_btns[key] = btn

    # ── 바람 패널 ─────────────────────────────────────────────────────
    def _build_wind_panel(self):
        self.wind_panel = Panel(self.row1, self.L("wind_panel"),
            lambda: self._toggle_panel("wind"), bg=BG2)
        self.wind_panel.pack(side="left", fill="both", expand=True,
            padx=(0,4), pady=0)

        b = self.wind_panel.body

        # 기수/진북 토글
        mode_f = tk.Frame(b, bg=BG2)
        mode_f.pack(fill="x", pady=(0,6))
        self.wp_hdg = tk.Label(mode_f, text=self.L("hdg_up"),
            font=FB, bg=ACCENT, fg=WHITE, cursor="hand2", padx=12, pady=3)
        self.wp_hdg.pack(side="left", expand=True, fill="x", padx=(0,2))
        self.wp_hdg.bind("<Button-1>", lambda e: self._set_mode(True))
        self.wp_nth = tk.Label(mode_f, text=self.L("nth_up"),
            font=FB, bg=BG3, fg=DIM, cursor="hand2", padx=12, pady=3)
        self.wp_nth.pack(side="left", expand=True, fill="x")
        self.wp_nth.bind("<Button-1>", lambda e: self._set_mode(False))

        # 나침반 캔버스
        self.wcanv = tk.Canvas(b, width=200, height=200,
            bg=BG2, highlightthickness=0)
        self.wcanv.pack()

        # 풍향/풍속 수치
        vals = tk.Frame(b, bg=BG2)
        vals.pack(fill="x", pady=(6,0))

        left = tk.Frame(vals, bg=BG2)
        left.pack(side="left", expand=True)
        tk.Label(left, text=self.L("wind_dir"), font=FS, bg=BG2, fg=DIM).pack()
        self.wdir_lbl = tk.Label(left, text="---°", font=FV, bg=BG2, fg=ORANGE)
        self.wdir_lbl.pack()

        right = tk.Frame(vals, bg=BG2)
        right.pack(side="left", expand=True)
        tk.Label(right, text=self.L("wind_spd"), font=FS, bg=BG2, fg=DIM).pack()
        self.wspd_lbl = tk.Label(right, text="-- kt", font=FV, bg=BG2, fg=ORANGE)
        self.wspd_lbl.pack()

        # 정면풍/크로스윈드
        comp = tk.Frame(b, bg=BG2)
        comp.pack(fill="x", pady=(6,0))

        hw_f = tk.Frame(comp, bg=BG2)
        hw_f.pack(side="left", expand=True)
        tk.Label(hw_f, text=self.L("headwind"), font=FS, bg=BG2, fg=DIM).pack()
        self.hw_lbl = tk.Label(hw_f, text="-- kt", font=FM, bg=BG2, fg=GREEN)
        self.hw_lbl.pack()

        cw_f = tk.Frame(comp, bg=BG2)
        cw_f.pack(side="left", expand=True)
        tk.Label(cw_f, text=self.L("crosswind"), font=FS, bg=BG2, fg=DIM).pack()
        self.cw_lbl = tk.Label(cw_f, text="-- kt", font=FM, bg=BG2, fg=YELLOW)
        self.cw_lbl.pack()

        # Beaufort 바
        self.bft_lbl = tk.Label(b, text="", font=FS, bg=BG2, fg=DIM)
        self.bft_lbl.pack(pady=(4,0))

        # 풍향 안내 — 화살표 방향 설명
        tk.Label(b, text="→ 화살촉 = 바람이 밀어가는 방향", font=FXS, bg=BG2, fg=DIM).pack(pady=(2,0))
        tk.Label(b, text="숫자 = 바람이 불어오는 방향(FROM)", font=FXS, bg=BG2, fg=DIM).pack()

    # ── 비행 데이터 패널 ──────────────────────────────────────────────
    def _build_data_panel(self):
        self.data_panel = Panel(self.row1, self.L("data_panel"),
            lambda: self._toggle_panel("data"), bg=BG2)
        self.data_panel.pack(side="left", fill="both", expand=True,
            padx=(0,4), pady=0)

        b = self.data_panel.body
        self.data_cells = {}

        items = [
            [("oat","기온 OAT","--°C"), ("density","밀도고도","----ft"), ("alt_msl","고도 MSL","----ft")],
            [("alt_agl","고도 AGL","----ft"), ("ias","IAS","--kt"), ("tas","TAS","--kt")],
            [("vsi","VSI","--fpm"), ("qnh","QNH","--hPa"), ("rpm","RPM","----")],
        ]
        for row_items in items:
            row = tk.Frame(b, bg=BG2)
            row.pack(fill="x", pady=2)
            for key, label, default in row_items:
                cell = tk.Frame(row, bg=BG3, padx=8, pady=4)
                cell.pack(side="left", expand=True, fill="both", padx=2)
                tk.Label(cell, text=label, font=FXS, bg=BG3, fg=DIM).pack()
                val = tk.Label(cell, text=default, font=FM, bg=BG3, fg=WHITE)
                val.pack()
                self.data_cells[key] = val

        # 연료 게이지
        fuel_f = tk.Frame(b, bg=BG2)
        fuel_f.pack(fill="x", pady=(6,0))
        tk.Label(fuel_f, text=self.L("fuel"), font=FS, bg=BG2, fg=DIM).pack(side="left")
        self.fuel_val = tk.Label(fuel_f, text="-- gal", font=FM, bg=BG2, fg=WHITE)
        self.fuel_val.pack(side="right")

        self.fuel_bar_frame = tk.Frame(b, bg=BG3, height=12)
        self.fuel_bar_frame.pack(fill="x", pady=(2,0))
        self.fuel_bar = tk.Frame(self.fuel_bar_frame, bg=GREEN, height=12)
        self.fuel_bar.place(x=0, y=0, relwidth=0.7, relheight=1)

        fuel_ef = tk.Frame(b, bg=BG2)
        fuel_ef.pack(fill="x")
        tk.Label(fuel_ef, text="E", font=FXS, bg=BG2, fg=DIM).pack(side="left")
        tk.Label(fuel_ef, text="F", font=FXS, bg=BG2, fg=DIM).pack(side="right")

        # RPM 게이지
        rpm_f = tk.Frame(b, bg=BG2)
        rpm_f.pack(fill="x", pady=(8,0))
        tk.Label(rpm_f, text="RPM", font=FS, bg=BG2, fg=DIM).pack(side="left")
        self.rpm_val2 = tk.Label(rpm_f, text="----", font=FM, bg=BG2, fg=WHITE)
        self.rpm_val2.pack(side="right")

        self.rpm_bar_frame = tk.Frame(b, bg=BG3, height=12)
        self.rpm_bar_frame.pack(fill="x", pady=(2,0))
        self.rpm_bar = tk.Frame(self.rpm_bar_frame, bg=ACCENT, height=12)
        self.rpm_bar.place(x=0, y=0, relwidth=0.5, relheight=1)

        rpm_ef = tk.Frame(b, bg=BG2)
        rpm_ef.pack(fill="x")
        tk.Label(rpm_ef, text="0", font=FXS, bg=BG2, fg=DIM).pack(side="left")
        tk.Label(rpm_ef, text="3000", font=FXS, bg=BG2, fg=DIM).pack(side="right")

    # ── 항법 패널 ─────────────────────────────────────────────────────
    def _build_nav_panel(self):
        self.nav_panel = Panel(self.row1, self.L("nav_panel"),
            lambda: self._toggle_panel("nav"), bg=BG2)
        self.nav_panel.pack(side="left", fill="both", expand=True,
            pady=0)

        b = self.nav_panel.body

        # 출발지
        home_f = tk.Frame(b, bg=BG3, padx=8, pady=6)
        home_f.pack(fill="x", pady=(0,4))
        hdr = tk.Frame(home_f, bg=BG3)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏠 " + self.L("home"), font=FB, bg=BG3, fg=WHITE).pack(side="left")
        self.set_home_btn = tk.Label(hdr, text=self.L("set_home"),
            font=FXS, bg=BG2, fg=ACCENT, cursor="hand2", padx=6)
        self.set_home_btn.pack(side="right")
        self.set_home_btn.bind("<Button-1>", lambda e: self._set_home())
        self.home_brg = tk.Label(home_f, text=f"{self.L('bearing')}: --  {self.L('distance')}: --",
            font=FN, bg=BG3, fg=DIM)
        self.home_brg.pack(anchor="w", pady=(2,0))

        # 목적지
        dest_f = tk.Frame(b, bg=BG3, padx=8, pady=6)
        dest_f.pack(fill="x", pady=(0,4))
        hdr2 = tk.Frame(dest_f, bg=BG3)
        hdr2.pack(fill="x")
        tk.Label(hdr2, text="🚩 " + self.L("dest"), font=FB, bg=BG3, fg=WHITE).pack(side="left")
        self.set_dest_btn = tk.Label(hdr2, text=self.L("set_dest"),
            font=FXS, bg=BG2, fg=YELLOW, cursor="hand2", padx=6)
        self.set_dest_btn.pack(side="right")
        self.set_dest_btn.bind("<Button-1>", lambda e: self._set_dest())
        self.dest_brg = tk.Label(dest_f, text=f"{self.L('bearing')}: --  {self.L('distance')}: --",
            font=FN, bg=BG3, fg=DIM)
        self.dest_brg.pack(anchor="w", pady=(2,0))

        # 현재 위치
        pos_f = tk.Frame(b, bg=BG3, padx=8, pady=6)
        pos_f.pack(fill="x")
        tk.Label(pos_f, text="📍 " + self.L("position"), font=FB, bg=BG3, fg=WHITE).pack(anchor="w")
        self.pos_lat = tk.Label(pos_f, text=f"{self.L('lat')}: --", font=FN, bg=BG3, fg=DIM)
        self.pos_lat.pack(anchor="w")
        self.pos_lon = tk.Label(pos_f, text=f"{self.L('lon')}: --", font=FN, bg=BG3, fg=DIM)
        self.pos_lon.pack(anchor="w")
        self.pos_alt = tk.Label(pos_f, text=f"{self.L('alt')}: --", font=FN, bg=BG3, fg=DIM)
        self.pos_alt.pack(anchor="w")

    # ── 공항 패널 ─────────────────────────────────────────────────────
    def _build_apt_panel(self):
        self.apt_panel = Panel(self.row2, self.L("apt_panel"),
            lambda: self._toggle_panel("apt"), bg=BG2)
        self.apt_panel.pack(side="left", fill="both", expand=True,
            padx=(0,4), pady=0)

        b = self.apt_panel.body

        # 헤더 행
        hdr = tk.Frame(b, bg=BG2)
        hdr.pack(fill="x", pady=(0,4))
        tk.Label(hdr, text="#", font=FXS, bg=BG2, fg=DIM, width=3).pack(side="left")
        tk.Label(hdr, text="ICAO", font=FXS, bg=BG2, fg=DIM, width=6).pack(side="left")
        tk.Label(hdr, text=self.L("apt_name"), font=FXS, bg=BG2, fg=DIM, width=20, anchor="w").pack(side="left")
        tk.Label(hdr, text=self.L("apt_dir"), font=FXS, bg=BG2, fg=DIM, width=10).pack(side="left")
        tk.Label(hdr, text=self.L("apt_dist"), font=FXS, bg=BG2, fg=DIM, width=8).pack(side="left")

        tk.Frame(b, bg=BORDER, height=1).pack(fill="x", pady=(0,4))

        self.apt_list_frame = tk.Frame(b, bg=BG2)
        self.apt_list_frame.pack(fill="both", expand=True)

    # ── POI 패널 ─────────────────────────────────────────────────────
    def _build_poi_panel(self):
        self.poi_panel = Panel(self.row2, self.L("poi_panel"),
            lambda: self._toggle_panel("poi"), bg=BG2)
        self.poi_panel.pack(side="left", fill="both", expand=True,
            pady=0)

        b = self.poi_panel.body

        # 입력 행
        inp_f = tk.Frame(b, bg=BG2)
        inp_f.pack(fill="x", pady=(0,6))

        self.poi_entry = tk.Entry(inp_f, font=FN, bg=BG3, fg=WHITE,
            insertbackground=WHITE, relief="flat", bd=4)
        self.poi_entry.pack(side="left", fill="x", expand=True, padx=(0,6))

        save_btn = tk.Label(inp_f, text=self.L("save_btn"),
            font=FB, bg=ACCENT, fg=WHITE, cursor="hand2", padx=8, pady=4)
        save_btn.pack(side="left")
        save_btn.bind("<Button-1>", lambda e: self._save_poi_from_entry())

        # 정렬 버튼
        sort_f = tk.Frame(b, bg=BG2)
        sort_f.pack(fill="x", pady=(0,4))
        tk.Label(sort_f, text=f"저장된 POI ({len(self.pois)}개)",
            font=FS, bg=BG2, fg=DIM).pack(side="left")

        # POI 목록
        self.poi_list_frame = tk.Frame(b, bg=BG2)
        self.poi_list_frame.pack(fill="both", expand=True)
        self._rebuild_poi_list()

    # ── 패널 토글 ────────────────────────────────────────────────────
    def _toggle_panel(self, key):
        self.panel_visible[key] = not self.panel_visible[key]

        # row1 패널들 순서대로 재배치
        for f in [self.wind_panel, self.data_panel, self.nav_panel]:
            f.pack_forget()
        for k, f in [("wind", self.wind_panel),
                     ("data", self.data_panel),
                     ("nav",  self.nav_panel)]:
            if self.panel_visible.get(k):
                pad = 0 if k == "nav" else 4
                f.pack(side="left", fill="both", expand=True,
                       padx=(0, pad), pady=0)

        # row2 패널들 순서대로 재배치
        for f in [self.apt_panel, self.poi_panel]:
            f.pack_forget()
        for k, f in [("apt", self.apt_panel),
                     ("poi", self.poi_panel)]:
            if self.panel_visible.get(k):
                pad = 4 if k == "apt" else 0
                f.pack(side="left", fill="both", expand=True,
                       padx=(0, pad), pady=0)

        # 토글 버튼 색 업데이트
        if key in self.toggle_btns:
            self.toggle_btns[key].config(
                bg=ACCENT if self.panel_visible[key] else BG3)

    def _toggle_expand(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.compact_bar.pack_forget()
            self.main_frame.pack(fill="both", expand=True, padx=8, pady=(0,8))
        else:
            self.main_frame.pack_forget()
            self.compact_bar.pack(fill="x")

    # ── 언어/모드 ────────────────────────────────────────────────────
    def _toggle_lang(self):
        self.lc = "en" if self.lc=="ko" else "ko"
        self._save_cfg()
        self.lang_btn.config(text=self.L("lang_btn"))
        messagebox.showinfo("SkyMark",
            "언어 변경은 다음 실행부터 적용됩니다.\nLanguage change applies on next launch.")

    def _set_alpha(self, val):
        self.root.attributes("-alpha", int(val)/100)

    def _set_mode(self, hu):
        self.hdg_up = hu
        self.hdg_btn.config(bg=ACCENT if hu else BG3, fg=WHITE if hu else DIM)
        self.nth_btn.config(bg=ACCENT if not hu else BG3, fg=WHITE if not hu else DIM)
        self.wp_hdg.config(bg=ACCENT if hu else BG3, fg=WHITE if hu else DIM)
        self.wp_nth.config(bg=ACCENT if not hu else BG3, fg=WHITE if not hu else DIM)

    # ── 홈/목적지 ────────────────────────────────────────────────────
    def _set_home(self):
        if not self.ok: return
        n = simpledialog.askstring(self.L("set_home"), self.L("enter_name"),
                                   initialvalue="Home Base")
        if n:
            self.home = {"lat":self.lat,"lon":self.lon,"name":n}
            self._save_cfg()

    def _set_dest(self):
        if not self.ok: return
        n = simpledialog.askstring(self.L("set_dest"), self.L("enter_name"),
                                   initialvalue="Destination")
        if n:
            self.dest = {"lat":self.lat,"lon":self.lon,"name":n}
            self._save_cfg()

    # ── POI ──────────────────────────────────────────────────────────
    def _save_poi_from_entry(self):
        if not self.ok: return
        name = self.poi_entry.get().strip()
        if not name:
            name = simpledialog.askstring(self.L("poi_panel"), self.L("enter_name"))
        if name:
            self.pois.insert(0, {
                "name": name,
                "lat":  round(self.lat,6),
                "lon":  round(self.lon,6),
                "alt":  round(self.msl,0),
                "saved_at": time.strftime("%Y-%m-%d %H:%M")
            })
            self._save_pois()
            self.poi_entry.delete(0, tk.END)
            self._rebuild_poi_list()

    def _del_poi(self, i):
        if messagebox.askyesno("", self.L("del_confirm")):
            self.pois.pop(i)
            self._save_pois()
            self._rebuild_poi_list()

    def _open_earth(self, la, lo):
        webbrowser.open(f"https://earth.google.com/web/@{la},{lo},1000a,5000d,35y,0h,45t,0r")

    def _rebuild_poi_list(self):
        for w in self.poi_list_frame.winfo_children(): w.destroy()
        if not self.pois:
            tk.Label(self.poi_list_frame, text=self.L("no_poi"),
                font=FN, bg=BG2, fg=DIM).pack(pady=8)
            return
        for i, p in enumerate(self.pois[:8]):
            row = tk.Frame(self.poi_list_frame, bg=BG3, padx=6, pady=4)
            row.pack(fill="x", pady=2)

            # 아이콘 + 이름
            left = tk.Frame(row, bg=BG3)
            left.pack(side="left", fill="x", expand=True)
            tk.Label(left, text="📍 "+p["name"], font=FB, bg=BG3, fg=WHITE).pack(anchor="w")

            # 방향/거리
            info = ""
            if self.ok and self.lat != 0:
                d,b = haversine(self.lat,self.lon,p["lat"],p["lon"])
                rv = rel_brg(b,self.hdg)
                info = f"{brg_txt(rv,LANG[self.lc])}  {d:.1f} {self.L('nm')}"
            tk.Label(left, text=p.get("saved_at","") + ("  "+info if info else ""),
                font=FXS, bg=BG3, fg=DIM).pack(anchor="w")

            # 버튼들
            right = tk.Frame(row, bg=BG3)
            right.pack(side="right")
            eb = tk.Label(right, text="🌍", font=("맑은 고딕",12),
                bg=BG3, fg=ACCENT, cursor="hand2")
            eb.pack(side="left", padx=2)
            eb.bind("<Button-1>", lambda e,p=p: self._open_earth(p["lat"],p["lon"]))
            db = tk.Label(right, text="🗑", font=("맑은 고딕",12),
                bg=BG3, fg=RED, cursor="hand2")
            db.pack(side="left", padx=2)
            db.bind("<Button-1>", lambda e,x=i: self._del_poi(x))

    # ── 나침반 ───────────────────────────────────────────────────────
    def _draw_compass(self):
        c = self.wcanv; c.delete("all")
        cx=100; cy=100; r=85
        hu=self.hdg_up; wf=self.wdir; sp=self.wspd; hd=self.hdg

        # 배경 원
        c.create_oval(cx-r,cy-r,cx+r,cy+r, fill=BG3, outline=BORDER, width=2)

        # 눈금
        for a in range(0,360,30):
            rad=math.radians(a); tk2=10 if a%90==0 else 5
            c.create_line(cx+(r-tk2)*math.sin(rad),cy-(r-tk2)*math.cos(rad),
                          cx+r*math.sin(rad),cy-r*math.cos(rad),
                          fill=BORDER,width=2 if a%90==0 else 1)

        if not hu:
            for t,ax,ay in [("N",cx,cy-r-14),("S",cx,cy+r+14),
                              ("E",cx+r+14,cy),("W",cx-r-14,cy)]:
                stext(c,ax,ay,t,("맑은 고딕",10,"bold"),WHITE)
            ha=math.radians(hd)
            # 기체 아이콘
            stext(c,cx,cy,"✈",("맑은 고딕",18),WHITE)
            # 헤딩 선
            for i in range(16):
                t0,t1=i/16*0.75,(i+0.5)/16*0.75
                if i%2==0:
                    c.create_line(cx+r*t0*math.sin(ha),cy-r*t0*math.cos(ha),
                                  cx+r*t1*math.sin(ha),cy-r*t1*math.cos(ha),
                                  fill=ACCENT,width=2)
            tip_x=cx+r*0.82*math.sin(ha); tip_y=cy-r*0.82*math.cos(ha)
            p=ha+math.pi/2
            c.create_polygon(tip_x,tip_y,
                tip_x-10*math.sin(ha)+5*math.cos(p),tip_y+10*math.cos(ha)+5*math.sin(p),
                tip_x-10*math.sin(ha)-5*math.cos(p),tip_y+10*math.cos(ha)-5*math.sin(p),
                fill=ACCENT)
            wind_angle=wf
        else:
            for t,ag in [(self.L("fwd"),0),(self.L("rgt"),90),
                         (self.L("aft"),180),(self.L("lft"),270)]:
                a=math.radians(ag)
                stext(c,cx+(r+14)*math.sin(a),cy-(r+14)*math.cos(a),
                    t,("맑은 고딕",10,"bold"),WHITE)
            # 기수 삼각형
            c.create_polygon(cx,cy-r+2,cx-10,cy-r+20,cx+10,cy-r+20,fill=ACCENT)
            stext(c,cx,cy,"✈",("맑은 고딕",18),WHITE)
            wind_angle=wf-hd

        # 바람 화살표
        wa=math.radians(wind_angle)
        col = wind_color(sp)
        from_x=cx+r*0.65*math.sin(wa); from_y=cy-r*0.65*math.cos(wa)
        to_x  =cx-r*0.65*math.sin(wa); to_y  =cy+r*0.65*math.cos(wa)
        c.create_line(from_x,from_y,to_x,to_y,fill="#000",width=6)
        c.create_line(from_x,from_y,to_x,to_y,fill=col,width=3,
            arrow=tk.LAST,arrowshape=(14,17,6))
        c.create_oval(cx-5,cy-5,cx+5,cy+5,fill=col,outline="")

        # 기수 기준 모드에서 방향 텍스트
        if hu and sp > 0.5:
            rel=wind_angle%360
            if rel>180: rel-=360
            if   abs(rel)<=20:  desc=self.L("headwind_lbl")
            elif abs(rel)>=160: desc=self.L("tailwind_lbl")
            elif rel>0:         desc=f"{self.L('right')} {rel:.0f}°"
            else:               desc=f"{self.L('left')} {abs(rel):.0f}°"
            stext(c,cx,cy+r+20,desc,("맑은 고딕",10,"bold"),col)

    # ── 공항 목록 업데이트 ───────────────────────────────────────────
    def _update_apts(self):
        for w in self.apt_list_frame.winfo_children(): w.destroy()

        if self.apt_status == "loading":
            tk.Label(self.apt_list_frame, text="공항 데이터 로딩 중...",
                font=FN, bg=BG2, fg=DIM).pack(pady=8)
            return
        if self.apt_status == "fail":
            tk.Label(self.apt_list_frame, text=self.L("apt_download_fail"),
                font=FN, bg=BG2, fg=ORANGE).pack(pady=8)
            return
        if not self.ok or not self.apts: return

        sc=[]
        for a in self.apts:
            try:
                d,b=haversine(self.lat,self.lon,a["lat"],a["lon"])
                sc.append((d,b,a))
            except: pass
        sc.sort(key=lambda x:x[0])

        for i,(d,b,a) in enumerate(sc[:8]):
            rv=rel_brg(b,self.hdg)
            bl=brg_txt(rv,LANG[self.lc])
            col = ORANGE if rv%360<180 else ACCENT

            row=tk.Frame(self.apt_list_frame, bg=BG2 if i%2==0 else BG3)
            row.pack(fill="x", pady=1)

            tk.Label(row, text=str(i+1), font=FXS, bg=row["bg"], fg=DIM, width=3).pack(side="left")
            tk.Label(row, text=a["icao"], font=FB, bg=row["bg"], fg=WHITE, width=6).pack(side="left")
            tk.Label(row, text=a["name"][:22], font=FXS, bg=row["bg"], fg=DIM, width=22, anchor="w").pack(side="left")
            tk.Label(row, text=bl, font=FB, bg=row["bg"], fg=col, width=10).pack(side="left")
            tk.Label(row, text=f"{d:.1f}{self.L('nm')}", font=FB, bg=row["bg"], fg=WHITE, width=8).pack(side="left")

            eb=tk.Label(row, text="🌍", font=("맑은 고딕",11),
                bg=row["bg"], fg=ACCENT, cursor="hand2")
            eb.pack(side="right", padx=4)
            eb.bind("<Button-1>",lambda e,a=a: self._open_earth(a["lat"],a["lon"]))

    # ── 요약 바 업데이트 ─────────────────────────────────────────────
    def _update_summary(self):
        if not self.ok: return
        d,s=self.wdir,self.wspd
        self.sum_lbls["wind_sum"].config(text=f"✈ {d:.0f}° {s:.1f}kt", fg=wind_color(s))
        self.sum_lbls["oat_sum"].config(text=f"🌡 {self.oat:+.0f}°C")
        self.sum_lbls["alt_sum"].config(text=f"▲ {self.msl:,.0f}ft")
        self.sum_lbls["ias_sum"].config(text=f"IAS {self.ias:.0f}kt")
        self.sum_lbls["tas_sum"].config(text=f"TAS {self.tas:.0f}kt")
        self.sum_lbls["rpm_sum"].config(text=f"RPM {self.rpm:,.0f}")
        fu=self.fl+self.fr
        self.sum_lbls["fuel_sum"].config(text=f"⛽ {fu:.1f}gal",
            fg=RED if fu<3 else ORANGE if fu<6 else WHITE)
        if self.home:
            d2,b2=haversine(self.lat,self.lon,self.home["lat"],self.home["lon"])
            self.sum_lbls["home_sum"].config(text=f"🏠 {d2:.1f}{self.L('nm')}")
        if self.dest:
            d3,b3=haversine(self.lat,self.lon,self.dest["lat"],self.dest["lon"])
            self.sum_lbls["dest_sum"].config(text=f"🚩 {d3:.1f}{self.L('nm')}")

    # ── 메인 틱 ──────────────────────────────────────────────────────
    def _tick(self):
        if self.ok:
            self.conn_dot.config(fg=GREEN)
            self.conn_lbl.config(text=self.L("connected"), fg=GREEN)

            d,s,hd=self.wdir,self.wspd,self.hdg

            # 바람 패널
            self.wdir_lbl.config(text=f"{d:.1f}°", fg=wind_color(s))
            self.wspd_lbl.config(text=f"{s:.1f} kt", fg=wind_color(s))
            self.bft_lbl.config(text=f"{bft(s)}  (Beaufort {self._bft_num(s)})")

            # 정면풍/크로스윈드 계산
            rel=(d-hd+360)%360
            if rel>180: rel-=360
            hw = abs(s*math.cos(math.radians(rel)))
            cw = abs(s*math.sin(math.radians(rel)))
            hw_sign = "-" if rel>90 or rel<-90 else "+"
            self.hw_lbl.config(text=f"{hw_sign}{hw:.1f} kt",
                fg=RED if hw>15 else ORANGE if hw>8 else GREEN)
            self.cw_lbl.config(text=f"{cw:.1f} kt",
                fg=RED if cw>15 else ORANGE if cw>8 else YELLOW)

            # 데이터 패널
            self.data_cells["oat"].config(text=f"{self.oat:+.1f}°C",
                fg=ORANGE if self.oat>30 else WHITE)
            self.data_cells["density"].config(text=f"{self.da:,.0f} ft",
                fg=RED if self.da>self.msl+1000 else WHITE)
            self.data_cells["alt_msl"].config(text=f"{self.msl:,.0f} ft")
            self.data_cells["alt_agl"].config(text=f"{self.agl:,.0f} ft")
            self.data_cells["ias"].config(text=f"{self.ias:.1f} kt")
            self.data_cells["tas"].config(text=f"{self.tas:.1f} kt")
            vsi_col=RED if abs(self.vsi)>1500 else ORANGE if abs(self.vsi)>800 else GREEN
            self.data_cells["vsi"].config(text=f"{self.vsi:+.0f} fpm", fg=vsi_col)
            self.data_cells["qnh"].config(text=f"{self.qnh*33.8639:.0f} hPa")
            self.data_cells["rpm"].config(text=f"{self.rpm:,.0f}")
            fu=self.fl+self.fr
            self.fuel_val.config(text=f"{fu:.1f} gal",
                fg=RED if fu<3 else ORANGE if fu<6 else WHITE)
            self.rpm_val2.config(text=f"{self.rpm:,.0f}")

            # 연료/RPM 게이지
            fuel_pct = min(fu/24.0, 1.0)
            rpm_pct  = min(self.rpm/2800.0, 1.0)
            self.fuel_bar.place(relwidth=fuel_pct)
            self.fuel_bar.config(bg=RED if fuel_pct<0.15 else ORANGE if fuel_pct<0.3 else GREEN)
            self.rpm_bar.place(relwidth=rpm_pct)

            # 항법 패널
            if self.home:
                d2,b2=haversine(self.lat,self.lon,self.home["lat"],self.home["lon"])
                rv=rel_brg(b2,hd)
                self.home_brg.config(
                    text=f"{self.L('bearing')}: {brg_txt(rv,LANG[self.lc])}   {self.L('distance')}: {d2:.1f} {self.L('nm')}",
                    fg=WHITE)
            if self.dest:
                d3,b3=haversine(self.lat,self.lon,self.dest["lat"],self.dest["lon"])
                rv=rel_brg(b3,hd)
                self.dest_brg.config(
                    text=f"{self.L('bearing')}: {brg_txt(rv,LANG[self.lc])}   {self.L('distance')}: {d3:.1f} {self.L('nm')}",
                    fg=WHITE)

            # 위치
            lat_d=int(abs(self.lat)); lat_m=(abs(self.lat)-lat_d)*60
            lon_d=int(abs(self.lon)); lon_m=(abs(self.lon)-lon_d)*60
            self.pos_lat.config(
                text=f"{self.L('lat')}: {lat_d}° {lat_m:.2f}' {'N' if self.lat>=0 else 'S'}")
            self.pos_lon.config(
                text=f"{self.L('lon')}: {lon_d}° {lon_m:.2f}' {'E' if self.lon>=0 else 'W'}")
            self.pos_alt.config(text=f"{self.L('alt')}: {self.msl:,.0f} ft")

            # 나침반
            if self.panel_visible.get("wind"):
                self._draw_compass()

            # 공항/POI는 10초마다만 업데이트 (성능 최적화)
            self._tick_count += 1
            if self._tick_count % 10 == 0:
                if self.panel_visible.get("apt"):
                    self._update_apts()
                if self.panel_visible.get("poi"):
                    self._rebuild_poi_list()
            elif self._tick_count == 1:
                # 첫 번째 틱에는 바로 업데이트
                if self.panel_visible.get("apt"):
                    self._update_apts()
                if self.panel_visible.get("poi"):
                    self._rebuild_poi_list()

            # 요약 바
            if not self.expanded:
                self._update_summary()

        else:
            self.conn_dot.config(fg=ORANGE)
            self.conn_lbl.config(text=self.L("waiting"), fg=DIM)

        self.root.after(1000, self._tick)

    @staticmethod
    def _bft_num(kt):
        for i,limit in enumerate([1,4,7,11,17,22,28,34]):
            if kt<limit: return i
        return 12

    # ── SimConnect 폴링 ──────────────────────────────────────────────
    def _poll(self):
        sm=aq=None
        while self.running:
            if not self.ok:
                try:
                    sm=SimConnect(); aq=AircraftRequests(sm,_time=200)
                    self.ok=True
                except: time.sleep(3); continue
            try:
                def g(k): return aq.get(k)
                wd=g("AMBIENT_WIND_DIRECTION"); ws=g("AMBIENT_WIND_VELOCITY")
                hd=g("PLANE_HEADING_DEGREES_MAGNETIC")
                la=g("PLANE_LATITUDE");  lo=g("PLANE_LONGITUDE")
                ot=g("AMBIENT_TEMPERATURE"); da=g("DENSITY_ALTITUDE")
                ms=g("PLANE_ALTITUDE");  ag=g("PLANE_ALT_ABOVE_GROUND")
                ia=g("AIRSPEED_INDICATED"); ta=g("AIRSPEED_TRUE")
                vs=g("VERTICAL_SPEED")
                fl=g("FUEL_TANK_LEFT_MAIN_QUANTITY")
                fr=g("FUEL_TANK_RIGHT_MAIN_QUANTITY")
                rp=g("GENERAL_ENG_RPM:1"); qh=g("KOHLSMAN_SETTING_HG")

                if wd is not None: self.wdir=float(wd)
                if ws is not None: self.wspd=float(ws)
                if hd is not None: self.hdg=math.degrees(float(hd))%360
                if la is not None:
                    v=float(la); self.lat=math.degrees(v) if abs(v)<4 else v
                if lo is not None:
                    v=float(lo); self.lon=math.degrees(v) if abs(v)<4 else v
                if ot is not None: self.oat=float(ot)
                if da is not None: self.da =float(da)
                if ms is not None: self.msl=float(ms)
                if ag is not None: self.agl=float(ag)
                if ia is not None: self.ias=float(ia)
                if ta is not None: self.tas=float(ta)
                if vs is not None: self.vsi=float(vs)
                if fl is not None: self.fl =float(fl)
                if fr is not None: self.fr =float(fr)
                if rp is not None: self.rpm=float(rp)
                if qh is not None: self.qnh=float(qh)
                time.sleep(0.5)
            except: self.ok=False; sm=aq=None; time.sleep(3)

    # ── 드래그 ───────────────────────────────────────────────────────
    def _ds(self,e):
        self._dx=e.x_root-self.root.winfo_x()
        self._dy=e.y_root-self.root.winfo_y()

    def _dm(self,e):
        x=e.x_root-self._dx; y=e.y_root-self._dy
        self.root.geometry(f"+{x}+{y}")

    def _close(self):
        self.running=False; self._save_cfg(); self.root.destroy()


if __name__=="__main__":
    if not SC_OK:
        r=tk.Tk(); r.withdraw()
        messagebox.showerror("SkyMark",
            "SimConnect not found.\n\npip install SimConnect")
        r.destroy()
    else:
        print("SkyMark v2.0"); print("MSFS 2024 조종석 진입 후 실행하세요.")
        SkyMark()
