"""ADO 2 - Leis de Newton e Aplicações | versão web com Streamlit."""
from __future__ import annotations
import math
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

G_PADRAO = 9.81

st.set_page_config(page_title="ADO 2 — Simulador de Física", page_icon="⚙️", layout="wide")
st.title("Simulador Interativo — Leis de Newton")
st.caption("ADO 2 · Mecânica e Física Moderna · Ciência da Computação")
st.markdown("Altere os parâmetros nos controles. Os gráficos e os resultados são recalculados automaticamente usando as fórmulas fechadas da atividade.")


def calcular_plano(m1: float, m2: float, theta_graus: float, mu: float, g: float = G_PADRAO):
    theta = math.radians(theta_graus)
    normal = m1 * g * math.cos(theta)
    forca_motriz = m2 * g - m1 * g * math.sin(theta)
    mu_critico = abs(forca_motriz) / normal if normal > 0 else math.inf
    if abs(forca_motriz) <= mu * normal:
        aceleracao = 0.0
        estado = "Equilíbrio estático"
    else:
        sinal = 1 if forca_motriz > 0 else -1
        aceleracao = (forca_motriz - mu * normal * sinal) / (m1 + m2)
        estado = "Em movimento"
    tracao = m2 * (g - aceleracao)
    return {"normal": normal, "forca_motriz": forca_motriz, "mu_critico": mu_critico,
            "aceleracao": aceleracao, "tracao": tracao, "estado": estado}


def calcular_circular(raio: float, velocidade: float, massa: float):
    omega = velocidade / raio
    return {"omega": omega, "forca": massa * velocidade**2 / raio, "periodo": 2 * math.pi / omega}


def calcular_arrasto(massa: float, coeficiente: float, g: float, modelo: str):
    if modelo == "Linear":
        vt = massa * g / coeficiente
        tau = massa / coeficiente
        t95 = -tau * math.log(0.05)
    else:
        vt = math.sqrt(massa * g / coeficiente)
        t95 = (vt / g) * math.atanh(0.95)
    return {"terminal": vt, "t95": t95}

with st.sidebar:
    st.header("Configuração")
    sistema = st.radio("Sistema físico", ["Plano inclinado", "Força centrípeta", "Força de arrasto"])
    st.divider()
    st.caption("Os valores iniciais são exemplos. Use os controles para explorar outros cenários.")

if sistema == "Plano inclinado":
    st.subheader("Plano inclinado com atrito e tração")
    a, b, c, d = st.columns(4)
    with a: m1 = st.slider("Massa m₁ (kg)", 1.0, 20.0, 5.0, 0.5)
    with b: m2 = st.slider("Massa m₂ (kg)", 1.0, 20.0, 3.0, 0.5)
    with c: theta_graus = st.slider("Ângulo θ (°)", 0.0, 80.0, 30.0, 1.0)
    with d: mu = st.slider("Atrito μ (μs = μk)", 0.0, 1.0, 0.08, 0.01)
    r = calcular_plano(m1, m2, theta_graus, mu)
    t = np.linspace(0, 10, 500)
    x = 0.5 * r["aceleracao"] * t**2  # MRUV com x0 = v0 = 0.
    v = r["aceleracao"] * t  # MRUV: v(t) = v0 + at.
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Posição x tempo", "Velocidade x tempo"))
    fig.add_trace(go.Scatter(x=t, y=x, mode="lines", name="Posição x(t)"), row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=v, mode="lines", name="Velocidade v(t)"), row=1, col=2)
    fig.update_xaxes(title_text="Tempo (s)")
    fig.update_yaxes(title_text="Posição (m)", row=1, col=1)
    fig.update_yaxes(title_text="Velocidade (m/s)", row=1, col=2)
    fig.update_layout(height=450, margin=dict(l=20, r=20, t=60, b=20), legend=dict(orientation="h", y=-0.22))
    st.plotly_chart(fig, use_container_width=True)
    mcol = st.columns(4)
    mcol[0].metric("Aceleração", f"{r['aceleracao']:.4f} m/s²")
    mcol[1].metric("Tração no fio", f"{r['tracao']:.3f} N")
    mcol[2].metric("Atrito crítico μ crítico", f"{r['mu_critico']:.4f}")
    mcol[3].metric("Estado", r["estado"])
    with st.expander("Como esses valores são calculados"):
        st.latex(r"N=m_1g\cos\theta")
        st.latex(r"F_{\mathrm{motriz}}=m_2g-m_1g\sin\theta")
        st.latex(r"a=\frac{F_{\mathrm{motriz}}-\mu_kN\,\mathrm{sign}(F_{\mathrm{motriz}})}{m_1+m_2}")
        st.latex(r"x(t)=\frac{1}{2}at^2,\qquad v(t)=at,\qquad T=m_2(g-a)")
        st.write("A atividade sugere usar μs = μk para simplificar. O equilíbrio estático ocorre quando |Fmotriz| ≤ μs N.")

elif sistema == "Força centrípeta":
    st.subheader("Força centrípeta — movimento circular uniforme")
    a, b, c = st.columns(3)
    with a: R = st.slider("Raio R (m)", 0.5, 10.0, 2.0, 0.1)
    with b: vel = st.slider("Velocidade tangencial v (m/s)", 0.5, 20.0, 4.0, 0.1)
    with c: massa = st.slider("Massa m (kg)", 0.1, 10.0, 3.0, 0.1)
    r = calcular_circular(R, vel, massa)
    t = np.linspace(0, 3 * r["periodo"], 240)
    ang = r["omega"] * t
    xs, ys = R * np.cos(ang), R * np.sin(ang)
    frames = []
    # O Plotly anima o ponto ao longo da trajetória no navegador; a curva é x=R cos(ωt), y=R sin(ωt).
    for i in range(len(t)):
        frames.append(go.Frame(name=str(i), data=[go.Scatter(x=[xs[i]], y=[ys[i]], mode="markers", marker=dict(size=13))], traces=[1]))
    fig = go.Figure(data=[
        go.Scatter(x=xs, y=ys, mode="lines", name="Trajetória circular"),
        go.Scatter(x=[xs[0]], y=[ys[0]], mode="markers", name="Objeto", marker=dict(size=13)),
    ], frames=frames)
    fig.update_layout(
        height=520, title="Trajetória do objeto no plano x-y",
        xaxis=dict(title="x (m)", range=[-1.25*R, 1.25*R], scaleanchor="y", scaleratio=1),
        yaxis=dict(title="y (m)", range=[-1.25*R, 1.25*R]),
        margin=dict(l=20, r=20, t=60, b=20),
        updatemenus=[dict(type="buttons", showactive=False, x=0.02, y=1.12,
            buttons=[dict(label="▶ Animar", method="animate", args=[None, {"frame": {"duration": 35, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}]),
                     dict(label="⏸ Pausar", method="animate", args=[[None], {"mode": "immediate", "frame": {"duration": 0, "redraw": False}, "transition": {"duration": 0}}])])]
    )
    st.plotly_chart(fig, use_container_width=True)
    mcol = st.columns(3)
    mcol[0].metric("Força centrípeta", f"{r['forca']:.3f} N")
    mcol[1].metric("Velocidade angular ω", f"{r['omega']:.3f} rad/s")
    mcol[2].metric("Período", f"{r['periodo']:.3f} s")
    with st.expander("Como esses valores são calculados"):
        st.latex(r"\omega=\frac{v}{R},\qquad x(t)=R\cos(\omega t),\qquad y(t)=R\sin(\omega t)")
        st.latex(r"F_c=\frac{mv^2}{R}=m\omega^2R")

else:
    st.subheader("Força de arrasto — queda vertical")
    a, b, c = st.columns(3)
    with a: modelo = st.selectbox("Modelo", ["Linear", "Quadrático"])
    with b: massa = st.slider("Massa m (kg)", 0.5, 20.0, 5.0, 0.1)
    if modelo == "Linear":
        with c: coef = st.slider("Coeficiente b (kg/s)", 0.1, 5.0, 0.8, 0.1)
        nome = "b"
    else:
        with c: coef = st.slider("Coeficiente c (kg/m)", 0.01, 2.0, 0.8, 0.01)
        nome = "c"
    g = st.slider("Gravidade g (m/s²)", 1.0, 15.0, 9.81, 0.1)
    r = calcular_arrasto(massa, coef, g, modelo)
    vt, t95 = r["terminal"], r["t95"]
    tmax = max(5.0, 1.25 * t95)
    t = np.linspace(0, tmax, 500)
    if modelo == "Linear":
        tau = massa / coef
        v_drag = vt * (1 - np.exp(-t / tau))  # Solução fechada para F_arrasto = -b v.
        y_drag = vt * (t - tau * (1 - np.exp(-t / tau)))
    else:
        v_drag = vt * np.tanh(g * t / vt)  # Solução fechada para F_arrasto = -c v|v|.
        y_drag = (vt**2 / g) * np.log(np.cosh(g * t / vt))
    v_livre = g * t  # Queda livre a partir do repouso: v=gt.
    y_livre = 0.5 * g * t**2
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Distância de queda x tempo", "Velocidade x tempo"))
    fig.add_trace(go.Scatter(x=t, y=y_drag, mode="lines", name=f"Com arrasto {modelo.lower()}"), row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=y_livre, mode="lines", line=dict(dash="dash"), name="Queda livre"), row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=v_drag, mode="lines", name=f"Com arrasto {modelo.lower()}"), row=1, col=2)
    fig.add_trace(go.Scatter(x=t, y=v_livre, mode="lines", line=dict(dash="dash"), name="Sem arrasto: v=gt"), row=1, col=2)
    fig.add_hline(y=vt, line_dash="dot", annotation_text="Velocidade terminal", row=1, col=2)
    fig.update_xaxes(title_text="Tempo (s)")
    fig.update_yaxes(title_text="Distância (m)", row=1, col=1)
    fig.update_yaxes(title_text="Velocidade (m/s)", row=1, col=2)
    fig.update_layout(height=470, margin=dict(l=20, r=20, t=60, b=20), legend=dict(orientation="h", y=-0.22))
    st.plotly_chart(fig, use_container_width=True)
    mcol = st.columns(3)
    mcol[0].metric("Velocidade terminal", f"{vt:.3f} m/s")
    mcol[1].metric("Tempo para 95% de v terminal", f"{t95:.3f} s")
    mcol[2].metric("Coeficiente de arrasto", f"{coef:.3f} {('kg/s' if nome == 'b' else 'kg/m')}")
    with st.expander("Como esses valores são calculados"):
        if modelo == "Linear":
            st.latex(r"v_t=\frac{mg}{b},\qquad \tau=\frac{m}{b}")
            st.latex(r"v(t)=v_t(1-e^{-t/\tau})")
            st.latex(r"y(t)=v_t[t-\tau(1-e^{-t/\tau})]")
        else:
            st.latex(r"v_t=\sqrt{\frac{mg}{c}}")
            st.latex(r"v(t)=v_t\tanh\left(\frac{gt}{v_t}\right)")
            st.latex(r"y(t)=\frac{v_t^2}{g}\ln\cosh\left(\frac{gt}{v_t}\right)")
        st.write("A queda livre mostrada para comparação usa v(t)=gt e y(t)=½gt².")

st.divider()
st.caption("Modelo idealizado para fins didáticos. No plano inclinado, adota-se μs = μk, conforme a simplificação sugerida na atividade.")
