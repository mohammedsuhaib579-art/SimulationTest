import random
import time
from typing import Dict, List

import altair as alt
import pandas as pd
import streamlit as st

# --- Global configuration (Hugging Face friendly) --------------------------------
st.set_page_config(
    page_title="Clean Energy Founder Lab",
    page_icon="🌱",
    layout="wide",
)

THEME = """
<style>
body, .main {
    background: linear-gradient(140deg, #02070c 0%, #041926 30%, #012d3d 70%, #063238 100%);
    color: #f3f7fb;
    animation: aurora 18s ease-in-out infinite;
}
.stMetric, .stDataFrame, .stTable {
    border-radius: 14px;
}
.score-card {
    padding: 1.25rem;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0px 10px 35px rgba(0, 0, 0, 0.35);
    animation: floaty 6s ease-in-out infinite;
}
.glow {
    text-shadow: 0 0 18px rgba(24, 217, 182, 0.4);
    animation: pulse 3s ease-in-out infinite;
}
.section-label {
    letter-spacing: 0.25rem;
    font-size: 0.7rem;
    opacity: 0.7;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.12);
    border-radius: 999px;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(255,255,255,0.2);
}
.chips span {
    padding: 0.2rem 0.7rem;
    background: rgba(255,255,255,0.1);
    border-radius: 999px;
    margin-right: 0.4rem;
}
.animated-card {
    position: relative;
    overflow: hidden;
    border-radius: 18px;
    padding: 1.2rem;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.08);
    animation: cardGlow 5s ease-in-out infinite;
}
.animated-card::after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    border: 1px solid rgba(24,217,182,0.35);
    opacity: 0;
    animation: cardPulse 4s infinite;
}
.entry-overlay {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 9999;
    width: 420px;
    height: 240px;
    backdrop-filter: blur(12px);
    background: rgba(4,25,38,0.82);
    border: 2px solid rgba(24,217,182,0.5);
    border-radius: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: overlayFade 0.4s ease-out forwards;
}
.studio {
    width: 360px;
    height: 180px;
    position: relative;
}
.desk {
    position: absolute;
    width: 100%;
    height: 55px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    bottom: 60px;
}
.teammate {
    position: absolute;
    width: 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
    animation: bob 3s ease-in-out infinite;
}
.teammate .head {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #f6bd60;
    margin-bottom: 6px;
}
.teammate .body {
    width: 48px;
    height: 52px;
    border-radius: 18px;
    background: #1E88E5;
    position: relative;
    overflow: hidden;
}
.teammate .laptop {
    width: 48px;
    height: 32px;
    background: #90caf9;
    border-radius: 6px;
    border: 2px solid #0d47a1;
    position: absolute;
    top: 12px;
    animation: typing 0.8s ease-in-out infinite;
}
.teammate:nth-child(2) .body,
.teammate:nth-child(2) .laptop {
    background: #EC407A;
    border-color: #880E4F;
}
.teammate:nth-child(3) .body,
.teammate:nth-child(3) .laptop {
    background: #26A69A;
    border-color: #004D40;
}
.teammate:nth-child(4) .body,
.teammate:nth-child(4) .laptop {
    background: #FF7043;
    border-color: #BF360C;
}
.teammate:nth-child(1) { left: 10px; animation-delay: 0s; }
.teammate:nth-child(2) { left: 95px; animation-delay: 0.15s; }
.teammate:nth-child(3) { left: 190px; animation-delay: 0.3s; }
.teammate:nth-child(4) { left: 275px; animation-delay: 0.45s; }
.entry-caption {
    position: absolute;
    bottom: -30px;
    width: 100%;
    text-align: center;
    font-size: 0.85rem;
    letter-spacing: 0.2rem;
    color: #18d9b6;
}
@keyframes aurora {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes pulse {
    0%,100% { opacity: 0.85; }
    50% { opacity: 1; }
}
@keyframes floaty {
    0%,100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}
@keyframes cardGlow {
    0%,100% { box-shadow: 0 8px 25px rgba(0,0,0,0.25); }
    50% { box-shadow: 0 12px 40px rgba(24,217,182,0.25); }
}
@keyframes cardPulse {
    0% { opacity: 0; transform: scale(0.95); }
    50% { opacity: 0.5; transform: scale(1.05); }
    100% { opacity: 0; transform: scale(0.95); }
}
@keyframes bob {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}
@keyframes typing {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
}
@keyframes overlayFade {
    from { opacity: 0; transform: translate(-50%, -60%); }
    to { opacity: 1; transform: translate(-50%, -50%); }
}
</style>
"""
st.markdown(THEME, unsafe_allow_html=True)


# --- Simulation constants --------------------------------------------------------
SECTORS = ["Solar", "Wind", "Hydro", "Bioenergy"]
DEPARTMENTS = {
    "Engineering": {"salary": 140_000, "hire_cost": 25_000, "fire_cost": 10_000},
    "Marketing": {"salary": 110_000, "hire_cost": 18_000, "fire_cost": 8_000},
    "Sales": {"salary": 100_000, "hire_cost": 15_000, "fire_cost": 6_000},
    "Operations": {"salary": 95_000, "hire_cost": 12_000, "fire_cost": 4_000},
}
GLOBAL_EVENTS = [
    "oil_crisis",
    "tech_disruption",
    "talent_war",
    "policy_subsidy",
    "none",
]


# --- Player model ----------------------------------------------------------------
class Player:
    def __init__(self, name: str):
        self.name = name
        self.cash = 1_250_000
        self.total_revenue = 0
        self.liquidation_value = 0
        self.round = 1
        self.max_rounds = 12
        self.last_events: Dict[str, str] = {}
        self.workforce = {
            dept: {"count": 5 if dept != "Operations" else 3, "morale": 0.72}
            for dept in DEPARTMENTS
        }
        self.sectors: Dict[str, Dict[str, float]] = {
            sector: {"market_share": 0.0, "tech_level": 1.0, "active": False}
            for sector in SECTORS
        }
        self.workforce_log: List[Dict[str, float]] = []

    def _wage_run_rate(self) -> float:
        annual = sum(
            data["count"] * DEPARTMENTS[dept]["salary"]
            for dept, data in self.workforce.items()
        )
        return annual / 12

    def _team_multiplier(self) -> Dict[str, float]:
        eng_bonus = 1 + (self.workforce["Engineering"]["count"] * 0.015)
        marketing_bonus = 1 + (self.workforce["Marketing"]["count"] * 0.012)
        sales_bonus = 1 + (self.workforce["Sales"]["count"] * 0.01)
        ops_discount = max(0.75, 1 - (self.workforce["Operations"]["count"] * 0.007))
        return {
            "engineering": eng_bonus,
            "marketing": marketing_bonus,
            "sales": sales_bonus,
            "ops": ops_discount,
        }

    def get_market_price(self) -> float:
        sector_value = sum(
            self.calculate_liquidation_value(s)
            for s in self.sectors
            if self.sectors[s]["active"]
        )
        team_premium = (
            sum(d["count"] for d in self.workforce.values()) * 60_000
        )
        return (self.total_revenue + self.liquidation_value + sector_value + team_premium) * 1.15

    def get_sector_demand(self, sector: str) -> float:
        base = {"Solar": 0.55, "Wind": 0.45, "Hydro": 0.35, "Bioenergy": 0.28}[sector]
        volatility = {
            "Solar": random.uniform(0.6, 1.4),
            "Wind": random.choice([0.85, 1.0, 1.3]),
            "Hydro": random.uniform(0.9, 1.1),
            "Bioenergy": random.uniform(0.4, 2.0),
        }[sector]
        demand = min(base * volatility, 1.0)
        demand = max(0.05, demand)
        return demand

    def calculate_liquidation_value(self, sector: str) -> float:
        multipliers = {"Solar": 3.2, "Wind": 2.6, "Hydro": 1.8, "Bioenergy": 2.9}
        base_value = 900_000
        ms = self.sectors[sector]["market_share"]
        tl = self.sectors[sector]["tech_level"]
        return ms * tl * multipliers[sector] * base_value

    def _log_workforce(self):
        snapshot = {dept: data["count"] for dept, data in self.workforce.items()}
        snapshot["round"] = self.round
        self.workforce_log.append(snapshot)

    def apply_workforce_plan(self, plan: Dict[str, Dict[str, int]]) -> None:
        hr_messages = []
        for dept, changes in plan.items():
            target_delta = changes.get("net_change", 0)
            training = changes.get("training", 0)
            if training > 0:
                morale_boost = min(0.12, training / 200_000)
                self.workforce[dept]["morale"] = min(
                    1.1, self.workforce[dept]["morale"] + morale_boost
                )
                self.cash -= training
            if target_delta == 0:
                continue
            abs_delta = abs(target_delta)
            cost_key = "hire_cost" if target_delta > 0 else "fire_cost"
            cash_impact = abs_delta * DEPARTMENTS[dept][cost_key]
            if target_delta > 0 and self.cash < cash_impact:
                hr_messages.append(f"{dept}: hire denied (cash).")
                continue
            self.cash -= cash_impact
            self.workforce[dept]["count"] = max(
                0, self.workforce[dept]["count"] + target_delta
            )
            direction = "hired" if target_delta > 0 else "released"
            hr_messages.append(f"{dept}: {abs_delta} {direction}")
        if hr_messages:
            self.last_events["HR"] = " | ".join(hr_messages)

    def process_decisions(
        self,
        investments: Dict[str, float],
        prices: Dict[str, int],
        productions: Dict[str, int],
        active_sectors: List[str],
        exit_sectors: List[str],
        all_players_active_sectors: List[set],
        global_event: str,
        workforce_plan: Dict[str, Dict[str, int]],
    ) -> float:
        self.last_events = {}
        self.apply_workforce_plan(workforce_plan)
        payroll = self._wage_run_rate()
        self.cash -= payroll
        self.last_events["Payroll"] = f"Monthly payroll ${payroll:,.0f}"
        multipliers = self._team_multiplier()
        total_profit = 0.0
        entry_fee = 75_000

        for sector in SECTORS:
            if sector in exit_sectors and self.sectors[sector]["active"]:
                liquidation = self.calculate_liquidation_value(sector)
                self.cash += liquidation
                self.liquidation_value += liquidation
                self.sectors[sector] = {"market_share": 0.0, "tech_level": 1.0, "active": False}
                self.last_events[sector] = f"💰 Liquidated {sector} for ${liquidation:,.0f}"
                continue

            if sector not in active_sectors:
                self.sectors[sector]["active"] = False
                self.last_events[sector] = f"{sector}: on hold"
                continue

            if not self.sectors[sector]["active"]:
                if self.cash < entry_fee:
                    self.last_events[sector] = f"{sector}: entry blocked (cash)"
                    continue
                self.cash -= entry_fee
                self.sectors[sector]["active"] = True

            rd = investments.get(sector, 0)
            marketing = investments.get(f"{sector}_marketing", 0)
            price = prices.get(sector, 120)
            produced = productions.get(sector, 10_000)

            ops_multiplier = multipliers["ops"]
            cost = (rd + marketing + (produced * 55)) * ops_multiplier
            self.cash -= cost

            tech_gain = (rd / 100_000) * multipliers["engineering"]
            market_gain = (marketing / 120_000) * multipliers["marketing"]
            self.sectors[sector]["tech_level"] += tech_gain
            self.sectors[sector]["market_share"] = min(
                self.sectors[sector]["market_share"] + market_gain, 0.75
            )

            # Rivalry pressure
            rivals = sum(1 for s in all_players_active_sectors if sector in s)
            if rivals > 1:
                self.sectors[sector]["market_share"] *= 0.93

            # Global events
            if global_event == "oil_crisis" and sector == "Solar":
                self.sectors[sector]["market_share"] *= 1.15
            elif global_event == "tech_disruption":
                self.sectors[sector]["tech_level"] *= 0.92
            elif global_event == "policy_subsidy" and sector in ("Wind", "Hydro"):
                cost *= 0.9
            elif global_event == "talent_war":
                self.cash -= 15_000 * self.workforce["Engineering"]["count"]

            sector_event = random.choice(
                ["boom", "bust", "grid_upgrade", "weather", "none"]
            )
            if sector_event == "boom":
                self.sectors[sector]["market_share"] *= 1.18
                self.last_events[sector] = f"📈 {sector} boom"
            elif sector_event == "bust":
                self.sectors[sector]["market_share"] *= 0.82
                self.last_events[sector] = f"📉 {sector} bust"
            elif sector_event == "grid_upgrade" and sector in ("Wind", "Hydro"):
                self.sectors[sector]["tech_level"] *= 1.05
                self.last_events[sector] = f"⚡ Grid upgrade for {sector}"
            elif sector_event == "weather" and sector == "Solar":
                self.sectors[sector]["market_share"] *= 0.9
                self.last_events[sector] = f"🌧️ Weather hit {sector}"

            demand = self.get_sector_demand(sector) * multipliers["sales"]
            sold = min(produced, int(demand * 1_100_000))
            revenue = sold * price
            self.total_revenue += revenue
            profit = revenue - cost
            self.cash += profit
            total_profit += profit

        self._log_workforce()
        self.round += 1
        return total_profit


# --- Session bootstrap -----------------------------------------------------------
def bootstrap_session():
    defaults = {
        "num_players": 1,
        "players": [],
        "current_player": 0,
        "game_started": False,
        "history": [],
        "buyout_offer": None,
        "global_event": random.choice(GLOBAL_EVENTS),
        "sector_entry_animation": {"sector": None, "expires": 0},
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


bootstrap_session()


# --- Landing / setup -------------------------------------------------------------
st.markdown(
    """
<div class="score-card">
    <div class="section-label">FOUNDER LAB</div>
    <h1 class="glow">Next-Gen Clean Energy Simulation</h1>
    <p>Scale across Solar, Wind, Hydro and Bioenergy while architecting elite teams in Engineering, Marketing, Sales and Ops. Designed for Hugging Face Spaces & inspired by MIT's clean energy adventure.</p>
</div>
""",
    unsafe_allow_html=True,
)

if not st.session_state.game_started:
    with st.container():
        st.subheader("Configure Your Simulation")
        num_players = st.slider("Number of founders", 1, 4, 2)
        starting_cash = st.select_slider(
            "Capital Intensity",
            options=["Lean", "Balanced", "War Chest"],
            value="Balanced",
        )

        multiplier = {"Lean": 0.8, "Balanced": 1.0, "War Chest": 1.3}[starting_cash]
        if st.button("Launch Simulation", use_container_width=True):
            st.session_state.num_players = num_players
            st.session_state.players = [
                Player(f"Player {i + 1}") for i in range(num_players)
            ]
            for founder in st.session_state.players:
                founder.cash *= multiplier
            st.session_state.game_started = True
            st.rerun()
    st.stop()


# --- Active game -----------------------------------------------------------------
players = st.session_state.get("players") or []
if len(players) == 0:
    st.warning("Session reset detected — bootstrapping a fresh founder roster.")
    fallback_players = [
        Player(f"Player {i + 1}") for i in range(st.session_state.get("num_players", 1))
    ]
    st.session_state.players = fallback_players
    st.session_state.current_player = 0
    st.session_state.history = []
    st.session_state.buyout_offer = None
    st.session_state.game_started = False
    st.session_state.global_event = random.choice(GLOBAL_EVENTS)
    players = fallback_players

st.session_state.setdefault("sector_entry_animation", {"sector": None, "expires": 0})

current_player = st.session_state.current_player % len(players)
player = players[current_player]
global_event = st.session_state.get("global_event", random.choice(GLOBAL_EVENTS))
event_label = global_event.replace("_", " ").title()
if global_event != "none":
    st.info(f"🌍 Global Event: {event_label}")

all_players_active_sectors = [
    {s for s, data in p.sectors.items() if data["active"]} for p in players
]

animation_state = st.session_state.get("sector_entry_animation", {})
if animation_state.get("sector") and animation_state.get("expires", 0) > time.time():
    sector_name = animation_state["sector"]
    st.markdown(
        f"""
        <div class="entry-overlay">
            <div class="studio">
                <div class="desk"></div>
                <div class="teammate">
                    <div class="head"></div>
                    <div class="body"></div>
                    <div class="laptop"></div>
                </div>
                <div class="teammate">
                    <div class="head"></div>
                    <div class="body"></div>
                    <div class="laptop"></div>
                </div>
                <div class="teammate">
                    <div class="head"></div>
                    <div class="body"></div>
                    <div class="laptop"></div>
                </div>
                <div class="teammate">
                    <div class="head"></div>
                    <div class="body"></div>
                    <div class="laptop"></div>
                </div>
                <div class="entry-caption">IGNITING {sector_name.upper()} OPS</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
elif animation_state.get("sector"):
    st.session_state["sector_entry_animation"] = {"sector": None, "expires": 0}


# --- Leaderboard -----------------------------------------------------------------
st.subheader("🏆 Live Leaderboard")
leaderboard = (
    pd.DataFrame(
        [
            {
                "Player": p.name,
                "Cash": p.cash,
                "Total Revenue": getattr(p, "total_revenue", 0),
                "Liquidation Value": getattr(p, "liquidation_value", 0),
                "HR Bench": sum(d["count"] for d in p.workforce.values()),
                "Score": getattr(p, "total_revenue", 0)
                + getattr(p, "liquidation_value", 0),
            }
            for p in players
        ]
    )
    .sort_values("Score", ascending=False)
    .reset_index(drop=True)
)
st.dataframe(leaderboard, use_container_width=True)


# --- Buyout negotiations ---------------------------------------------------------
if st.session_state.buyout_offer:
    offer = st.session_state.buyout_offer
    buyer = players[offer["from"]]
    target = players[offer["to"]]
    st.markdown("### 💼 Pending Buyout")
    st.write(f"{buyer.name} → {target.name}")
    st.write(f"Offer: ${offer['amount']:,.0f} | Suggested: ${target.get_market_price():,.0f}")
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Accept Offer", key="accept_offer"):
            if buyer.cash >= offer["amount"]:
                buyer.cash -= offer["amount"]
                target.cash += offer["amount"]
                target.total_revenue += offer["amount"]
                for sector, data in target.sectors.items():
                    if data["active"]:
                        buyer.sectors[sector] = data.copy()
                players.remove(target)
                st.success(f"{target.name} exits. {buyer.name} absorbs assets.")
                st.session_state.buyout_offer = None
                st.rerun()
            else:
                st.error("Buyer lacks capital.")
    with btn_col2:
        if st.button("Decline Offer", key="decline_offer"):
            st.session_state.buyout_offer = None
            st.rerun()


# --- Sidebar decisions -----------------------------------------------------------
st.sidebar.header(f"{player.name} — Control Deck")
st.sidebar.metric("Cash", f"${player.cash:,.0f}")
st.sidebar.metric("Score", f"${player.total_revenue + player.liquidation_value:,.0f}")

investments: Dict[str, float] = {}
prices: Dict[str, int] = {}
productions: Dict[str, int] = {}
active_sectors: List[str] = []
exit_sectors: List[str] = []
workforce_plan: Dict[str, Dict[str, int]] = {
    dept: {"net_change": 0, "training": 0} for dept in DEPARTMENTS
}

with st.sidebar.expander("Sector Plays", expanded=True):
    for sector in SECTORS:
        enter_key = f"{player.name}_{sector}_enter"
        exit_key = f"{player.name}_{sector}_exit"
        rd_key = f"{player.name}_{sector}_rd"
        mkt_key = f"{player.name}_{sector}_mkt"
        price_key = f"{player.name}_{sector}_price"
        prod_key = f"{player.name}_{sector}_prod"
        anim_flag_key = f"{player.name}_{sector}_anim_flag"
        if anim_flag_key not in st.session_state:
            st.session_state[anim_flag_key] = False

        enter = st.checkbox(
            f"Activate {sector}",
            value=player.sectors[sector]["active"],
            key=enter_key,
        )
        if enter:
            active_sectors.append(sector)
            if (
                not player.sectors[sector]["active"]
                and not st.session_state[anim_flag_key]
            ):
                st.session_state["sector_entry_animation"] = {
                    "sector": sector,
                    "expires": time.time() + 5,
                }
                st.session_state[anim_flag_key] = True
            investments[sector] = st.slider(
                f"{sector} R&D",
                0,
                700_000,
                80_000,
                step=10_000,
                key=rd_key,
            )
            investments[f"{sector}_marketing"] = st.slider(
                f"{sector} Brand",
                0,
                600_000,
                50_000,
                step=10_000,
                key=mkt_key,
            )
            prices[sector] = st.slider(
                f"{sector} ASP",
                40,
                260,
                140,
                step=10,
                key=price_key,
            )
            productions[sector] = st.slider(
                f"{sector} Units",
                0,
                120_000,
                15_000,
                step=1_000,
                key=prod_key,
            )
            exit_sector = st.checkbox(
                f"Exit {sector}",
                value=False,
                key=exit_key,
            )
            if exit_sector:
                exit_sectors.append(sector)
        else:
            st.session_state[exit_key] = False
            st.session_state[anim_flag_key] = False

with st.sidebar.expander("People Ops", expanded=True):
    for dept in DEPARTMENTS:
        delta_key = f"{player.name}_{dept}_delta"
        train_key = f"{player.name}_{dept}_train"
        if delta_key not in st.session_state:
            st.session_state[delta_key] = 0
        if train_key not in st.session_state:
            st.session_state[train_key] = 0
        net_change = st.slider(
            f"{dept} hires (+) / exits (-)",
            min_value=-10,
            max_value=20,
            value=st.session_state[delta_key],
            key=delta_key,
        )
        training = st.number_input(
            f"{dept} training ($)",
            min_value=0,
            max_value=200_000,
            step=10_000,
            value=st.session_state[train_key],
            key=train_key,
        )
        workforce_plan[dept] = {"net_change": net_change, "training": training}

if len(players) > 1:
    st.sidebar.subheader("Strategic Buyout")
    opponent_names = [p.name for p in players if p != player]
    target_name = st.sidebar.selectbox(
        "Target founder", opponent_names, key=f"{player.name}_target"
    )
    if target_name:
        target_idx = next(i for i, p in enumerate(players) if p.name == target_name)
        suggested = players[target_idx].get_market_price()
        st.sidebar.caption(f"Suggested: ${suggested:,.0f}")
        offer_value = st.sidebar.number_input(
            "Offer ($)",
            min_value=0,
            value=int(suggested),
            step=50_000,
        )
        if st.sidebar.button("Send Offer"):
            st.session_state.buyout_offer = {
                "from": current_player,
                "to": target_idx,
                "amount": offer_value,
            }
            st.sidebar.success("Offer sent.")
else:
    st.sidebar.caption("Buyouts unlock with 2+ founders.")


# --- Main dashboard --------------------------------------------------------------
st.subheader(f"{player.name}'s Command Center — Round {player.round}/{player.max_rounds}")
dash_col1, dash_col2, dash_col3, dash_col4 = st.columns(4)
with dash_col1:
    st.metric("Cash", f"${player.cash:,.0f}")
with dash_col2:
    st.metric("Lifetime Revenue", f"${player.total_revenue:,.0f}")
with dash_col3:
    st.metric("Liquidation Value", f"${player.liquidation_value:,.0f}")
with dash_col4:
    st.metric("Total Headcount", int(sum(d["count"] for d in player.workforce.values())))

t1, t2, t3 = st.tabs(["Sector Ops", "Talent Intelligence", "Timeline"])

with t1:
    for sector in SECTORS:
        block = st.container()
        data = player.sectors[sector]
        state = "ACTIVE" if data["active"] else "IDLE"
        block.markdown(f"#### {sector} — {state}")
        st.progress(min(1.0, data["market_share"] / 0.75))
        block.metric("Market Share", f"{data['market_share']:.1%}")
        block.metric("Tech Level", f"{data['tech_level']:.2f}")

with t2:
    wf_df = pd.DataFrame(
        [
            {
                "Department": dept,
                "Headcount": stats["count"],
                "Morale": f"{stats['morale']*100:.0f}%",
                "Avg Salary": f"${DEPARTMENTS[dept]['salary']:,.0f}",
            }
            for dept, stats in player.workforce.items()
        ]
    )
    st.table(wf_df)

with t3:
    player_history = [
        h for h in st.session_state.history if h.get("Player") == player.name
    ]
    if player_history:
        hist_df = pd.DataFrame(player_history)
        chart = (
            alt.Chart(hist_df)
            .mark_line(point=True)
            .encode(
                x="Round",
                y=alt.Y("Cash", scale=alt.Scale(zero=False)),
                color=alt.value("#18d9b6"),
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.caption("Complete a round to unlock performance timelines.")


# --- Submit turn -----------------------------------------------------------------
if st.sidebar.button("Submit Round", use_container_width=True):
    if player.round <= player.max_rounds and player.cash > 0:
        profit = player.process_decisions(
            investments,
            prices,
            productions,
            active_sectors,
            exit_sectors,
            all_players_active_sectors,
            global_event,
            workforce_plan,
        )
        if profit >= 0:
            st.success(f"{player.name} posted +${profit:,.0f} profit.")
        else:
            st.error(f"{player.name} burned ${-profit:,.0f}.")

        st.session_state.history.append(
            {
                "Player": player.name,
                "Round": player.round - 1,
                "Cash": player.cash,
                "Revenue": player.total_revenue,
                "Liquidation": player.liquidation_value,
            }
        )

        for dept in DEPARTMENTS:
            st.session_state[f"{player.name}_{dept}_delta"] = 0
            st.session_state[f"{player.name}_{dept}_train"] = 0
        for sector in SECTORS:
            st.session_state[f"{player.name}_{sector}_anim_flag"] = False
            st.session_state[f"{player.name}_{sector}_exit"] = False

        st.session_state.current_player = (current_player + 1) % len(players)
        st.session_state.global_event = random.choice(GLOBAL_EVENTS)
        st.rerun()
    else:
        st.error(f"{player.name} is out of cash or rounds.")


# --- Events ticker ---------------------------------------------------------------
if player.last_events:
    st.subheader("🔥 This Round's Signals")
    for label, event in player.last_events.items():
        st.markdown(f"- **{label}** — {event}")


# --- End game --------------------------------------------------------------------
all_done = all(p.round > p.max_rounds or p.cash <= 0 for p in players)
if all_done or len(players) == 1:
    st.subheader("Final Scores")
    summary = sorted(
        players,
        key=lambda p: getattr(p, "total_revenue", 0) + getattr(p, "liquidation_value", 0),
        reverse=True,
    )
    winner = summary[0]
    st.balloons()
    st.success(
        f"{winner.name} wins with ${winner.total_revenue + winner.liquidation_value:,.0f}!"
    )
    if st.button("Restart Simulation", use_container_width=True):
        st.session_state.clear()
        st.rerun()
