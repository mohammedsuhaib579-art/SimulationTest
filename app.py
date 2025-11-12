import streamlit as st
import random
import pandas as pd

class Player:
    def __init__(self, name):
        self.name = name
        self.cash = 1000000
        self.sectors = {
            'Solar': {'market_share': 0.0, 'tech_level': 1.0, 'active': False},
            'Wind': {'market_share': 0.0, 'tech_level': 1.0, 'active': False},
            'Hydro': {'market_share': 0.0, 'tech_level': 1.0, 'active': False},
            'Bioenergy': {'market_share': 0.0, 'tech_level': 1.0, 'active': False}
        }
        self.round = 1
        self.max_rounds = 6  # Increased for longer games
        self.last_events = {}

    def get_sector_demand(self, sector):
        base_demands = {'Solar': 0.4, 'Wind': 0.3, 'Hydro': 0.2, 'Bioenergy': 0.1}
        demand = base_demands[sector]
        if sector == 'Solar':
            demand *= random.uniform(0.5, 1.5)  # Weather volatility
        elif sector == 'Wind':
            demand *= random.choice([0.8, 1.0, 1.3])  # Regulation factor
        elif sector == 'Hydro':
            demand *= random.uniform(0.9, 1.1)  # Stable
        elif sector == 'Bioenergy':
            demand *= random.uniform(0.3, 2.0)  # Emerging, high variance
        return min(demand, 1.0)

    def process_decisions(self, investments, prices, productions, active_sectors, all_players_active_sectors):
        total_profit = 0
        self.last_events = {}
        entry_fee = 50000  # Strategic entry cost, per PDF tactics
        for sector in self.sectors:
            if sector in active_sectors:
                if not self.sectors[sector]['active']:
                    if self.cash >= entry_fee:
                        self.cash -= entry_fee  # Pay to enter
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
                self.sectors[sector]['market_share'] = min(self.sectors[sector]['market_share'] + marketing / 100000, 0.4)  # Cap at 40%
                
                # Rivalry: Reduce MS if others are in the same sector
                rivals_in_sector = sum(1 for p in all_players_active_sectors if sector in p)
                if rivals_in_sector > 1:
                    self.sectors[sector]['market_share'] *= 0.95  # Slight penalty
                
                # Random event per sector (tied to PDF profiles)
                event = random.choice(["boom", "bust", "regulation", "weather", "none"])
                if event == "boom":
                    self.sectors[sector]['market_share'] *= 1.2
                    self.last_events[sector] = f"📈 {sector} Boom! Market surged."
                elif event == "bust":
                    self.sectors[sector]['market_share'] *= 0.8
                    self.last_events[sector] = f"📉 {sector} Bust! Market dropped."
                elif event == "regulation" and sector == 'Wind':
                    self.sectors[sector]['market_share'] *= 1.1
                    self.last_events[sector] = f"📜 Wind Regulation Boost!"
                elif event == "weather" and sector == 'Solar':
                    self.sectors[sector]['market_share'] *= 0.9
                    self.last_events[sector] = f"🌧️ Solar Weather Disruption!"
                else:
                    self.last_events[sector] = f"{sector}: Steady round."
                
                demand = self.get_sector_demand(sector)
                sold = min(produced, int(demand * 1000000))
                revenue = sold * price
                profit = revenue - cost
                self.cash += profit
                total_profit += profit
            else:
                self.sectors[sector]['active'] = False
                self.sectors[sector]['market_share'] = 0.0
                self.last_events[sector] = f"{sector}: Exited market."
        
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

# Streamlit App
st.title("Multi-Sector Clean Energy Startup Simulation")
st.markdown("Inspired by MIT Sloan & Market Profiles. Compete in 4 sectors: Solar, Wind, Hydro, Bioenergy!")

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

# Fixed: Correct list comprehension for active sectors
all_players_active_sectors = [set(s for s in p.sectors if p.sectors[s]['active']) for p in players]

# Leaderboard (Public Info)
st.subheader("🏆 Leaderboard (Public Results)")
leaderboard = pd.DataFrame([
    {
        'Player': p.name,
        'Cash': p.cash,
        'Total Market Share': sum(s['market_share'] for s in p.sectors.values()),
        'Dominant Sector': max(p.sectors, key=lambda s: p.sectors[s]['market_share']) if any(p.sectors[s]['market_share'] > 0 for s in p.sectors) else 'None'
    } for p in players
]).sort_values('Cash', ascending=False)
st.dataframe(leaderboard)

# Player Turn
st.subheader(f"{player.name}'s Turn - Round {player.round} / {player.max_rounds}")

# Sidebar for Decisions (Private)
st.sidebar.header(f"{player.name} - Decisions")
investments = {}
prices = {}
productions = {}
active_sectors = []
for sector in player.sectors:
    if st.sidebar.checkbox(f"Enter/Stay in {sector} (Entry Fee: $50k if new)", value=player.sectors[sector]['active']):
        active_sectors.append(sector)
        investments[sector] = st.sidebar.slider(f"{sector} R&D ($)", 0, 200000, 25000)
        prices[sector] = st.sidebar.slider(f"{sector} Price per Unit ($)", 50, 200, 100)
        productions[sector] = st.sidebar.slider(f"{sector} Units Produced", 0, 20000, 5000)

if st.sidebar.button("Submit Decisions & Next Turn"):
    if player.round <= player.max_rounds and player.cash > 0:
        profit = player.process_decisions(investments, prices, productions, active_sectors, all_players_active_sectors)
        st.success(f"{player.name}'s Round {player.round-1} Complete!")
        if profit > 0:
            st.success(f"🎉 Total Profit: ${profit:,.0f}!")
        elif profit < 0:
            st.error(f"💸 Total Loss: ${-profit:,.0f}!")
        
        # Update history
        st.session_state.history.append({
            'Player': player.name,
            'Round': player.round-1,
            'Cash': player.cash,
            'Sector Profits': {s: (investments.get(s, 0) * 0.1) for s in active_sectors}  # Simplified
        })
        
        # Next player
        st.session_state.current_player = (current_player + 1) % len(players)
        st.rerun()
    else:
        st.error(f"{player.name} is out!")

# Dashboard for Current Player
col1, col2 = st.columns(2)
with col1:
    st.metric("Cash", f"${player.cash:,.0f}")
with col2:
    total_ms = sum(s['market_share'] for s in player.sectors.values())
    st.metric("Total Market Share", f"{total_ms:.1%}")

for sector, data in player.sectors.items():
    if data['active']:
        st.write(f"**{sector}**: MS {data['market_share']:.1%}, Tech {data['tech_level']:.1f}")

# Events
if player.last_events:
    st.subheader("🔥 Sector Events")
    for sector, event in player.last_events.items():
        st.markdown(f"**{event}**")

# History (Player-Specific) - Fixed: Safe key access
if st.session_state.history:
    player_history = [h for h in st.session_state.history if isinstance(h, dict) and h.get('Player') == player.name]
    if player_history:
        df = pd.DataFrame(player_history)
        st.subheader(f"{player.name}'s History")
        st.dataframe(df)

# End Game
all_done = all(p.round > p.max_rounds or p.cash <= 0 for p in players)
if all_done:
    st.subheader("Game Over!")
    winners = sorted(players, key=lambda p: p.cash, reverse=True)
    st.write(f"Winner: {winners[0].name} with ${winners[0].cash:,.0f}")
    st.write(f"Loser: {winners[-1].name} with ${winners[-1].cash:,.0f}")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()
