import streamlit as st
import random
import pandas as pd

class CleanEnergyStartup:
    def __init__(self):
        self.cash = 1000000
        self.market_share = 0.05
        self.tech_level = 1.0
        self.round = 1
        self.max_rounds = 5
        self.last_event = "None"

    def get_demand(self):
        oil_price = random.uniform(50, 150)
        regulation_factor = random.choice([0.8, 1.0, 1.2])
        base_demand = 0.3
        demand = base_demand * (150 / oil_price) * regulation_factor
        return min(demand, 1.0)

    def process_decisions(self, rd_investment, marketing_spend, price_per_unit, units_produced):
        # Cap decisions
        rd_investment = min(rd_investment, self.cash * 0.5)
        marketing_spend = min(marketing_spend, self.cash * 0.3)
        units_produced = min(units_produced, 50000)

        total_cost = rd_investment + marketing_spend + (units_produced * 50)
        if total_cost > self.cash:
            rd_investment *= 0.5
            marketing_spend *= 0.5
            units_produced = int(self.cash / 50 * 0.8)
            total_cost = rd_investment + marketing_spend + (units_produced * 50)

        self.cash -= total_cost

        # Effects
        self.tech_level += rd_investment / 100000
        market_boost = marketing_spend / 100000
        self.market_share = min(self.market_share + market_boost, 0.5)

        # Random event
        event = random.choice(["tech_breakthrough", "competition", "regulation", "none"])
        if event == "tech_breakthrough":
            self.tech_level += 0.5
            self.last_event = "⚡ Technological Breakthrough! Tech level increased."
        elif event == "competition":
            self.market_share *= 0.9
            self.last_event = "⚠️ New Competitor! Market share decreased."
        elif event == "regulation":
            self.market_share *= 1.1
            self.last_event = "📜 Favorable Regulations! Market share increased."
        else:
            self.last_event = "No major event this round."

        # Calculate outcomes
        demand = self.get_demand()
        units_sold = min(units_produced, int(demand * 1000000))
        revenue = units_sold * price_per_unit
        profit = revenue - total_cost
        self.cash += profit

        # Update history for graphs
        st.session_state.history.append({
            'Round': self.round,
            'Cash': self.cash,
            'Market Share': self.market_share,
            'Tech Level': self.tech_level,
            'Revenue': revenue,
            'Profit': profit
        })

        self.round += 1

        return units_sold, revenue, profit

# Initialize session state for persistence across runs (now after class definition)
if 'startup' not in st.session_state:
    st.session_state.startup = CleanEnergyStartup()
if 'history' not in st.session_state:
    st.session_state.history = []

# Streamlit App
st.title("Clean Energy Startup Simulation")
st.markdown("Inspired by MIT Sloan. Manage your startup over 5 rounds!")

startup = st.session_state.startup

# Sidebar for Decisions
st.sidebar.header("Round Decisions")
rd_investment = st.sidebar.slider("R&D Investment ($)", 0, 500000, 50000)
marketing_spend = st.sidebar.slider("Marketing Spend ($)", 0, 300000, 30000)
price_per_unit = st.sidebar.slider("Price per Unit ($)", 50, 200, 100)
units_produced = st.sidebar.slider("Units Produced", 0, 50000, 10000)

if st.sidebar.button("Submit Decisions & Advance Round"):
    if startup.round <= startup.max_rounds and startup.cash > 0:
        units_sold, revenue, profit = startup.process_decisions(rd_investment, marketing_spend, price_per_unit, units_produced)
        st.success(f"Round {startup.round-1} Complete!")
        # Profit/Loss Flares
        if profit > 0:
            st.success(f"🎉 Profit Alert: You made ${profit:,.0f} this round! Great job!")
        elif profit < 0:
            st.error(f"💸 Loss Alert: You incurred a loss of ${-profit:,.0f}. Adjust your strategy!")
        else:
            st.info("📊 Break-Even: No profit or loss this round.")
    else:
        st.error("Game Over!")

# Main Dashboard
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Cash", f"${startup.cash:,.0f}")
with col2:
    st.metric("Market Share", f"{startup.market_share:.1%}")
with col3:
    st.metric("Tech Level", f"{startup.tech_level:.1f}")

st.subheader(f"Round {startup.round} / {startup.max_rounds}")
st.write(f"Estimated Demand: {startup.get_demand():.1%}")

# More Prominent Events
if startup.last_event != "None":
    st.subheader("🔥 Round Event")
    st.markdown(f"**{startup.last_event}**")  # Bold and larger for prominence

# Results and History (Full History Now Visible)
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.subheader("Round Results (Full History)")
    st.dataframe(df)  # Shows all rounds, not just the latest

    # Simplified Trends
    st.subheader("Trends")
    st.line_chart(df.set_index('Round')[['Cash', 'Market Share']])  # Simple line chart

# End Game
if startup.round > startup.max_rounds or startup.cash <= 0:
    st.subheader("Game Over!")
    st.write(f"Final Cash: ${startup.cash:,.0f}")
    st.write(f"Final Market Share: {startup.market_share:.1%}")
    if startup.cash > 2000000:
        st.success("Success! Your startup thrived.")
    elif startup.cash > 500000:
        st.warning("Decent run. Try again for better results.")
    else:
        st.error("Failure. Learn from your decisions!")
    if st.button("Restart"):
        st.session_state.startup = CleanEnergyStartup()
        st.session_state.history = []
        st.rerun()
