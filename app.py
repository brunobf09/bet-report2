#Import
import streamlit as st
import betstats2

l=""
ligas=['','ARG - Argentina', 'AUT - Austria', 'BRA - Brazil','CHN - China','DNK - Denmark'
      ,'FIN - Finland','IRL - Ireland','JPN - Japan','MEX - Mexico',
      'NOR - Norway','POL - Poland', 'ROM - Romania',
      'RUS - Russia','SWE - Sweden','SWZ - Switzerland','USA - USA']

placeholder = st.empty()
placeholder.image("bet_fig.png")
#selectbox

options= st.selectbox('Select the League',ligas)

if options!="":
      l=options.split()[0]
      name = options.split()[2]
      placeholder.empty()


st.write('You selected:', options)


try:
      #Obtendo Dados e figuras
      var,descritive , vo, opp =betstats2.liga(l)
      var["Metrics"] = var.index.astype(str)
      var = var.reset_index()
      var = var.drop("index",axis=1)
      var = var.set_index("Metrics")
      var = var.drop("count",axis=0)


      #Header
      if options=='BRA - Brazil':
            st.image("https://www.futebolnaveia.com.br/wp-content/uploads/2022/03/Brasileirao-2022.jpg")
      else:
            st.image("https://tv2play.hu/assets/4/6/461830e3-7fe8-45ff-8737-19598e45748c/fileAsset/premier_league_cover.jpg")
      st.title(f'**{name} Analysis**')
      st.text('by: Bruno Brasil')

      #body
      # Primeira parte
      st.write(f'Report from {name} in order to beat the Betting Houses.')
      st.subheader('Historical and Current Bet Peformance')
      st.image('fig1.png')
      st.subheader('Performance Summary')
      st.table(var)

      # Segunda Parte
      st.subheader('Statistical Analysis')
      st.image('fig2.png')
      st.subheader('Descritive Analysis')
      st.table(descritive)
      st.subheader(vo)
      st.write(opp)

      # Terceira parte
      st.subheader('Strategy Results')
      st.image("fig3.png")

except:
      pass

if __name__ == "__main__":
    main()
