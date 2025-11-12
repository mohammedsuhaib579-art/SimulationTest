import streamlit as st
import random
import pandas as pd

class Player:
    def __init__(self, name):
        self.name = name
        self.cash = 1000000
        self.total_revenue = 0  # Track cumulative revenue
        self.sectors = {
            'Solar': {'market_share': 0.0, 'tech_level': 1.0, 'active': False},
            'Wind': {'market_share': 0.0, 'tech_level': 1.0, 'active': False},
            'Hydro': {'market_share': 0.0, 'tech_level': 1.0, 'active': False},
            'Bioenergy': {'market_share': 0.0, 'tech_level': 1.0, 'active': False}
        }
        self.round = 1
        self.max_rounds = 10  # Extended to 10 rounds
        self.last_events = {}
        self.liquidation_value = 0  # Total liquidation cash

    def calculate_liquidation_value(self, sector):
        # Boosted multipliers for higher earnings
        multipliers = {'Solar': 3.0, 'Wind': 2.0, 'Hydro': 1.5, 'Bioenergy': 2.5}
        base_value = 750000  # Increased base for more cash
        ms = self.sectors[sector]['market_share']
        tl = self.sectors[sector]['tech_level']
        return ms * tl * multipliers[sector] * base_value

    def get_market_price(self):
        # Suggested buyout price: Revenue + Liquidation + Sector values * premium
        sector_value = sum(self.calculate_liquidation_value(s) for s in self.sectors if self.sectors[s]['active'])
        return (self.total_revenue + self.liquidation_value + sector_value) * 1.2

    def get_sector_demand(self, sector):
        base_demands = {'Solar': 0.5, 'Wind': 0.4, 'Hydro': 0.3, 'Bioenergy': 0.2}  # Increased for more sales
        demand = base_demands[sector]
        if sector == 'Solar':
            demand *= random.uniform(0.5, 1.5)
        elif sector == 'Wind':
            demand *= random.choice([0.8, 1.0, 1.3])
        elif sector == 'Hydro':
            demand *= random.uniform(0.9, 1.1)
        elif sector == 'Bioenergy':
            demand *= random.uniform(0.3, 2.0)
        return min(demand, 1.0)

    def process_decisions(self, investments, prices, productions, active_sectors, exit_sectors, all_players_active_sectors, global_event):
        total_profit = 0
        self.last_events = {}
        entry_fee = 50000
        for sector in self.sectors:
            if sector in exit_sectors and self.sectors[sector]['active']:
                # Liquidate and exit
                liquidation = self.calculate_liquidation_value(sector)
                self.cash += liquidation
                self.liquidation_value += liquidation
                self.sectors[sector] = {'market_share': 0.0, 'tech_level': 1.0, 'active': False}
                self.last_events[sector] = f"💰 Liquidated {sector} for ${liquidation:,.0f}!"
                continue
            if sector in active_sectors:
                if not self.sectors[sector]['active']:
                    if self.cash >= entry_fee:
                        self.cash -= entry_fee
                        self.sectors[sector]['active'] = True
                    else:
                        self.last_events[sector] = f"{sector}: Insufficient funds to enter."
                        continue
                rd = investments.get(sector, 0)
                marketing = investments.get(sector, 0) * 0.5
                price = prices.get(sector, 100)
                produced = productions.get(sector, 0)
                
                cost = rd + marketing + (produced * 50)
                if cost > self.cash:
                    cost *= 0.5
                
                self.cash -= cost
                self.sectors[sector]['tech_level'] += rd / 100000
                self.sectors[sector]['market_share'] = min(self.sectors[sector]['market_share'] + marketing / 100000, 0.6)  # Higher cap
                
                # High-risk bonus for dominance
                if self.sectors[sector]['market_share'] > 0.5:
                    total_profit *= 1.2  # 20% bonus
                
                # Rivalry
                rivals_in_sector = sum(1 for p in all_players_active_sectors if sector in p)
                if rivals_in_sector > 1:
                    self.sectors[sector]['market_share'] *= 0.95
                
                # Global event impact
                if global_event == "oil_crisis":
                    self.sectors[sector]['market_share'] *= 1.2
                    self.last_events[sector] = f"🛢️ Oil Crisis Boosted {sector}!"
                elif global_event == "tech_disruption":
                    self.sectors[sector]['tech_level'] *= 0.9
                    self.last_events[sector] = f"🤖 Tech Disruption Hit {sector}!"
                
                # Sector events
                event = random.choice(["boom", "bust", "regulation", "weather", "none"])
                if event == "boom":
                    self.sectors[sector]['market_share'] *= 1.2
                    self.last_events[sector] = f"📈 {sector} Boom!"
                elif event == "bust":
                    self.sectors[sector]['market_share'] *= 0.8
                    self.last_events[sector] = f"📉 {sector} Bust!"
                elif event == "regulation" and sector == 'Wind':
                    self.sectors[sector]['market_share'] *= 1.1
                    self.last_events[sector] = f"📜 Wind Regulation Boost!"
                elif event == "weather" and sector == 'Solar':
                    self.sectors[sector]['market_share'] *= 0.9
                    self.last_events[sector] = f"🌧️ Solar Weather Disruption!"
                else:
                    self.last_events[sector] = f"{sector}: Steady."
                
                demand = self.get_sector_demand(sector)
                sold = min(produced, int(demand * 1000000))
                revenue = sold * price
                self.total_revenue += revenue
                profit = revenue - cost
                self.cash += profit
                total_profit += profit
            else:
                self.sectors[sector]['active'] = False
                self.last_events[sector] = f"{sector}: Inactive."
        
        self.round += 1
        return total_profit

# Initialize session state
if 'num_players' not in st.session_state:
    st.session_state.num_players = 1
if 'players' not in st.session_state:
    st.session_state.players = []
if 'current_player' not in st.session_state:
    st.session_state.current_player = 0
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'history' not in st.session_state:
    st.session_state.history = []
if 'buyout_offer' not in st.session_state:
    st.session_state.buyout_offer = None  # {'from': player_index, 'to': player_index, 'amount': int}

# Streamlit App
st.title("Multi-Sector Clean Energy Startup Simulation")
st.markdown("Compete, liquidate, and buyout! Winner by Revenue + Liquidation. High earnings & fair pricing!")

# Start Screen
if not st.session_state.game_started:
    st.subheader("Setup Game")
    num_players = st.slider("Number of Players", 1, 4, 1)
    if st.button("Start Game"):
        st.session_state.num_players = num_players
        st.session_state.players = [Player(f"Player {i+1}") for i in range(num_players)]
        st.session_state.game_started = True
        st.rerun()
    st.stop()

players = st.session_state.players
current_player = st.session_state.current_player
player = players[current_player]

# Global shake-up event
global_event = random.choice(["oil_crisis", "tech_disruption", "none"])
if global_event != "none":
    st.warning(f"🌍 Global Event: {global_event.replace('_', ' ').title()} affects all sectors!")

all_players_active_sectors = [set(s for s in p.sectors if p.sectors[s]['active']) for p in players]

# Leaderboard - Fixed: Safe attribute access
st.subheader("🏆 Leaderboard")
leaderboard = pd.DataFrame([
    {
        'Player': p.name,
        'Cash': p.cash,
        'Total Revenue': getattr(p, 'total_revenue', 0),
        'Liquidation Value': getattr(p, 'liquidation_value', 0),
        'Score (Rev + Liq)': getattr(p, 'total_revenue', 0) + getattr(p, 'liquidation_value', 0),
        'Dominant Sector': max(p.sectors, key=lambda s: p.sectors[s]['market_share']) if any(p.sectors[s]['market_share'] > 0 for s in p.sectors) else 'None'
    } for p in players
]).sort_values('Score (Rev + Liq)', ascending=False)
st.dataframe(leaderboard)

# Buyout Offer
if st.session_state.buyout_offer:
    offer = st.session_state.buyout_offer
    target = players[offer['to']]
    suggested_price = target.get_market_price()
    st.subheader(f"💼 Buyout Offer from {players[offer['from']].name} to {target.name}")
    st.write(f"Offer: ${offer['amount']:,.0f} | Suggested Market Price: ${suggested_price:,.0f}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Accept"):
            buyer = players[offer['from']]
            if buyer.cash >= offer['amount']:
                buyer.cash -= offer['amount']
                target.cash += offer['amount']
                target.total_revenue += offer['amount']  # Add to revenue for win calc
                # Transfer sectors and exit
                for s in target.sectors:
                    if target.sectors[s]['active']:
                        buyer.sectors[s] = target.sectors[s].copy()
                        buyer.sectors[s]['active'] = True
                players.remove(target)
                st.success(f"{target.name} sold and exited! {buyer.name} takes over.")
                st.session_state.buyout_offer = None
                st.rerun()
            else:
                st.error("Buyer has insufficient funds!")
    with col2:
        if st.button("Decline"):
            st.session_state.buyout_offer = None
            st.rerun()

# Player Turn
st.subheader(f"{player.name}'s Turn - Round {player.round} / {player.max_rounds}")

# Sidebar
st.sidebar.header(f"{player.name} - Decisions")
investments = {}
prices = {}
productions = {}
active_sectors = []
exit_sectors = []
for sector in player.sectors:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        enter = st.checkbox(f"Enter/Stay {sector}", value=player.sectors[sector]['active'], key=f"enter_{sector}")
        if enter:
            active_sectors.append(sector)
            investments[sector] = st.slider(f"{sector} R&D ($)", 0, 500000, 25000, key=f"rd_{sector}")  # Higher max
            prices[sector] = st.slider(f"{sector} Price ($)", 50, 200, 100, key=f"price_{sector}")
            productions[sector] = st.slider(f"{sector} Units", 0, 50000, 5000, key=f"prod_{sector}")  # Higher max
    with col2:
        if st.checkbox(f"Liquidate & Exit {sector}", key=f"exit_{sector}"):
            exit_sectors.append(sector)

# Buyout Offer
st.sidebar.subheader("Make Buyout Offer")
target_player = st.sidebar.selectbox("Target Player", [p.name for p in players if p != player])
suggested_price = players[next(i for i, p in enumerate(players) if p.name == target_player)].get_market_price()
st.sidebar.write(f"Suggested Market Price: ${suggested_price:,.0f}")
offer_amount = st.sidebar.number_input("Your Offer Amount ($)", min_value=0, value=int(suggested_price))
if st.sidebar.button("Send Offer"):
    target_index = next(i for i, p in enumerate(players) if p.name == target_player)
    st.session_state.buyout_offer = {'from': current_player, 'to': target_index, 'amount': offer_amount}
    st.sidebar.success("Offer sent!")

if st.sidebar.button("Submit Decisions & Next Turn"):
    if player.round <= player.max_rounds and player.cash > 0:
        profit = player.process_decisions(investments, prices, productions, active_sectors, exit_sectors, all_players_active_sectors, global_event)
        st.success(f"{player.name}'s Round Complete!")
        if profit > 0:
            st.success(f"🎉 Profit: ${profit:,.0f}!")
        elif profit < 0:
            st.error(f"💸 Loss: ${-profit:,.0f}!")
        
        st.session_state.history.append({
            'Player': player.name,
            'Round': player.round-1,
            'Cash': player.cash,
            'Revenue': getattr(player, 'total_revenue', 0),
            'Liquidation': getattr(player, 'liquidation_value', 0)
        })
        
        st.session_state.current_player = (current_player + 1) % len(players)
        st.rerun()
    else:
        st.error(f"{player.name} is out!")

# Dashboard
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Cash", f"${player.cash:,.0f}")
with col2:
    st.metric("Total Revenue", f"${getattr(player, 'total_revenue', 0):,.0f}")
with col3:
    st.metric("Liquidation Value", f"${getattr(player, 'liquidation_value', 0):,.0f}")

for sector, data in player.sectors.items():
    if data['active']:
        try:
            liq = player.calculate_liquidation_value(sector)
        except AttributeError:
            liq = 0  # Default if method fails
        st.write(f"**{sector}**: MS {data['market_share']:.1%}, Tech {data['tech_level']:.1f}, Est. Liq ${liq:,.0f}")

# Events
if player.last_events:
    st.subheader("🔥 Events")
    for sector, event in player.last_events.items():
        st.markdown(f"**{event}**")

# History
if st.session_state.history:
    player_history = [h for h in st.session_state.history if isinstance(h, dict) and h.get('Player') == player.name]
    if player_history:
        df = pd.DataFrame(player_history)
        st.subheader(f"{player.name}'s History")
        st.dataframe(df)

# End Game
all_done = all(p.round > p.max_rounds or p.cash <= 0 for p in players)
if all_done or len(players) == 1:
    st.subheader("Game Over!")
    winners = sorted(players, key=lambda p: getattr(p, 'total_revenue', 0) + getattr(p, 'liquidation_value', 0), reverse=True)
    winner = winners[0]
    loser = winners[-1] if len(winners) > 1 else None
    
    # Winner Celebration
    st.balloons()  # Party poppers
    st.markdown("""
    <style>
    .winner-bg {
        background-color: red !important;
        color: white !important;
        padding: 20px;
        text-align: center;
        font-size: 48px;
        font-weight: bold;
    }
    </style>
    <div class="winner-bg">🎉 YOU WIN! 🎉</div>
    """, unsafe_allow_html=True)
    st.success(f"Congratulations {winner.name}! Score: ${getattr(winner, 'total_revenue', 0) + getattr(winner, 'liquidation_value', 0):,.0f}")
    
    # Loser Message
    if loser:
        st.error(f"Better luck next time, {loser.name}. Score: ${getattr(loser, 'total_revenue', 0) + getattr(loser, 'liquidation_value', 0):,.0f}")
    
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
