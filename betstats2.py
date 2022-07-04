#Importando bibliotecas
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Importando dados
def liga(l):
  liga = pd.read_csv(f"https://www.football-data.co.uk/new/{l}.csv")
  liga.Date = liga.Date.apply(lambda x: int(x.split("/")[2]))
  liga = liga[liga.Date>=2022]
  liga = liga[['Country', 'Home', 'Away', 'HG', 'AG', 'Res', 'AvgH']]
  liga.columns = ['Div', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'B365H']
  liga.FTR = liga.FTR.map({'H':0, 'D':1, 'A':1})
  liga['bet']=liga.B365H.apply(lambda x: 0 if x <2 else 1)
  liga.reset_index(inplace=True, drop=True)

  book = pd.read_csv('https://www.dropbox.com/s/zfaoil639aruc1c/Book2.csv?dl=1')
  book.FTR = book.FTR.map({'H':0, 'D':1, 'A':1})
  book['bet']=book.B365H.apply(lambda x: 0 if x <2 else 1)
  hist = book[book.Div==liga.Div[0]]

  def var(liga, prob=True):
    variancia=[]
    proba=liga[liga.bet==0]
    if prob==False:
      for i in range(10,len(liga)):
        variancia.append(
            liga.iloc[0:i].FTR.value_counts()[0]/liga.iloc[0:i].FTR.value_counts()[1]
    )
    else:
      for i in range(3,len(proba)):
        variancia.append(
            proba.iloc[0:i].FTR.value_counts()[0]/len(proba[0:i])
        )
    return variancia

  #Criando os Dados
  var_liga = var(liga, prob=False)
  var_hist = var(hist,prob=False)
  prob_liga = var(liga,prob=True)
  prob_hist = var(hist,prob=True)
  # Dados com quantil
  var_hist_df = pd.concat([pd.DataFrame(var_hist,columns=["var_hist"]).describe(),
                           pd.DataFrame(var_hist,columns=["var_hist"]).quantile([0.025,0.975])])
  var_liga_df = pd.concat([pd.DataFrame(var_liga,columns=["var_liga"]).describe(),
                           pd.DataFrame(var_liga,columns=["var_liga"]).quantile([0.025,0.975])])
  prob_hist_df = pd.concat([pd.DataFrame(prob_hist,columns=["prob_hist"]).describe(),
                           pd.DataFrame(prob_hist,columns=["prob_hist"]).quantile([0.025,0.975])])
  prob_liga_df = pd.concat([pd.DataFrame(prob_liga,columns=["prob_liga"]).describe(),
                           pd.DataFrame(prob_liga,columns=["prob_liga"]).quantile([0.025,0.975])])

  df_list=[var_hist_df,var_liga_df,prob_hist_df,prob_liga_df]
  df = df_list[0]
  for df_ in df_list[1:]:
      df = df.join(df_, lsuffix=" ")


  #Criando um dataframe para as previsões corretas e erradas
  liga_acerto = liga[(liga.FTR==0) & (liga.B365H<2)]
  hist_acerto = hist[(hist.FTR==0) & (hist.B365H<2)]
  liga_erro = liga[(liga.FTR==1) & (liga.B365H<2)]
  media_acerto = liga_acerto.B365H.mean()
  desv_acerto = liga_acerto.B365H.std()


  #Dados descritivos atuais
  tx = 0.935
  mj_back = (1+(1 - prob_liga[-1])/(prob_liga[-1]*tx))
  mj_lay = (1+(1 - prob_liga[-1])*tx/(prob_liga[-1]))
  media_acerto = liga_acerto.B365H.mean()
  desv_acerto = liga_acerto.B365H.std()
  #Dados descritivos histórico
  macerto_hist = hist_acerto.B365H.mean()
  mjback_hist = (1+(1 - prob_hist[-1])/(prob_hist[-1]*tx))
  mjlay_hist = (1+(1 - prob_hist[-1])*tx/(prob_hist[-1]))
  desv_hist = hist_acerto.B365H.std()

  # print('Análise Descritiva')
  analise = {"Predictive Power": [prob_liga[-1]],
              "Fair Odd Back": [mj_back],
              "Fair Odd Lay": [mj_lay],
              "Correct Predictions Odd":[media_acerto],
              "Inferior Right Odd": [(media_acerto - desv_acerto)],
              "Superior Right Odd": [(media_acerto + desv_acerto)]}
  analise_hist = {"Predictive Power": [prob_hist[-1]],
              "Fair Odd Back": [mjback_hist],
              "Fair Odd Lay": [mjlay_hist],
              "Correct Predictions Odd":[macerto_hist],
              "Inferior Right Odd": [(macerto_hist - desv_hist)],
              "Superior Right Odd": [(macerto_hist + desv_hist)]}

  #DataFrame
  data = pd.DataFrame.from_dict(analise)
  data_hist = pd.DataFrame.from_dict(analise_hist)
  descritive = pd.concat([data_hist,data]).T
  descritive.columns = ["Historical Analysis","Current Analysis"]
  # descritive = descritive.apply(lambda x: round(x,2))

  #Text
  vo = f"Opportunity Analysis: \
  \n$V_{{{0}}}$ for Back Opportunity = {(mj_back-media_acerto):.2f} \
  \n$V_{{{0}}}$ for Lay Opportunity = {(mj_lay-media_acerto):.2f}"

  opp=''
  if mj_back-media_acerto < 0:
    opp = "You've got a Back Strategy opportunity"
  if mj_lay-media_acerto > 0:
    opp = "You've got a Lay Strategy opportunity"

#Plot figuras
  fig1,ax = plt.subplots(1,2,figsize=(16,5))
  ax[0].set_title("Relation Win X No Win", fontsize=16)
  ax[0].plot(var_liga[-200:])
  ax[0].plot(var_hist[-200:], alpha=0.8)
  ax[0].legend([f"Current Variation:{var_liga[-1]:.2f}",f"Historical Variation:{var_hist[-1]:.2f}"]);
  ax[1].set_title("Prediction Power", fontsize=16)
  ax[1].plot(prob_liga[-200:])
  ax[1].plot(prob_hist[-200:], alpha=0.8)
  ax[1].legend([f"Current Prediction:{prob_liga[-1]:.2f}",f"Historical Prediction:{prob_hist[-1]:.2f}"])
  fig1.tight_layout()
  fig1.savefig('fig1.png')

  #Plot Fig2
  fig2, ax= plt.subplots(1,3,figsize=(16,5))
  sns.kdeplot(liga_acerto.B365H,ax=ax[0], color="orange", linewidth=2)
  sns.kdeplot(liga_erro.B365H,ax=ax[0], color="green", linewidth=2)
  ax[0].legend(["Hits","Faults"])
  sns.boxplot(y=liga_acerto.B365H, ax=ax[1],color="orange")
  ax[0].set_title("Density Hits X Faults")
  ax[1].set_title("Boxplot Hits")
  sns.boxplot(y=liga_erro.B365H, ax=ax[2],color="green")
  ax[2].set_title("Boxplot Faults")
  fig2.tight_layout()
  fig2.savefig('fig2.png')

  #Plot fig3
  fig3, ax_1 = plt.subplots(3,2, figsize=(18,12))
  round = liga[liga.B365H<2].reset_index()
  ax_1[0,0].axhline(y = 0 , color="red",linestyle = '-',alpha=0.6)
  for r in range(4,11,2):
  #Apostas back com a bet
    resultado_favor=[]
    for i in range(len(round)):
      #se o resultado for 0 eu ganho 100% do valor da Odd-1
      if round.FTR[i]==0:
        resultado_favor.append(100*(round.B365H[i]-(1-r/100))*0.9362)
      #resultado 1 eu perco 100% do meu capital
      else:
        resultado_favor.append(-100)

    #Criando um gráfico para ver os resultados
    ax_1[0,0].plot(pd.Series(resultado_favor).cumsum(), lw=2)
    ax_1[0,0].set_title(f"Back Strategy odds < 2", fontsize=20)
    ax_1[0,0].legend(["Line 0","4%","6%","8%","10%"])
  for r in range(0,7,2):
    #Apostas lay com a bet
    resultado_contra=[]
    for i in range(len(round)):
      #se o resultado for 1 eu ganho 100% do capital investido
      if round.FTR[i]==1:
        resultado_contra.append(100*0.9362)
      #resultado 1 eu perco 100% da odd
      else:
        resultado_contra.append(-100*(round.B365H[i]-(1+r/100)))

    #Criando um gráfico para ver os resultados
    ax_1[0,1].axhline(y = 0 , color="red",linestyle = '-',alpha=0.6)
    ax_1[0,1].plot(pd.Series(resultado_contra).cumsum(), lw=2)
    ax_1[0,1].set_title(f"Lay Strategy odds < 2", fontsize=20)
    ax_1[0,1].legend(["Line 0", "0%","2%","4%","6%"])
  round = liga[(liga.B365H>1.6) & (liga.B365H<2)].reset_index()
  ax_1[1,0].axhline(y = 0 , color="red",linestyle = '-',alpha=0.6)
  for r in range(4,11,2):
  #Apostas back com a bet
    resultado_favor=[]
    for i in range(len(round)):
      #se o resultado for 0 eu ganho 100% do valor da Odd-1
      if round.FTR[i]==0:
        resultado_favor.append(100*(round.B365H[i]-(1-r/100))*0.9362)
      #resultado 1 eu perco 100% do meu capital
      else:
        resultado_favor.append(-100)

    #Criando um gráfico para ver os resultados
    ax_1[1,0].plot(pd.Series(resultado_favor).cumsum(), lw=2)
    ax_1[1,0].set_title(f"Back Strategy odds > 1.6", fontsize=20)
    ax_1[1,0].legend(["Line 0","4%","6%","8%","10%"])
  for r in range(0,7,2):
    #Apostas back com a bet
    resultado_contra=[]
    for i in range(len(round)):
      #se o resultado for 1 eu ganho 100% do capital investido
      if round.FTR[i]==1:
        resultado_contra.append(100*0.9362)
      #resultado 1 eu perco 100% da odd
      else:
        resultado_contra.append(-100*(round.B365H[i]-(1+r/100)))

    #Criando um gráfico para ver os resultados
    ax_1[1,1].axhline(y = 0 , color="red",linestyle = '-',alpha=0.6)
    ax_1[1,1].plot(pd.Series(resultado_contra).cumsum(),lw=2)
    ax_1[1,1].set_title(f"Lay Strategy odds > 1.6", fontsize=20)
    ax_1[1,1].legend(["Line 0", "0%","2%","4%","6%"])
  round = liga[liga.B365H<=1.6].reset_index()
  ax_1[2,0].axhline(y = 0 , color="red",linestyle = '-',alpha=0.6)
  for r in range(4,11,2):
  #Apostas back com a bet
    resultado_favor=[]
    for i in range(len(round)):
      #se o resultado for 0 eu ganho 100% do valor da Odd-1
      if round.FTR[i]==0:
        resultado_favor.append(100*(round.B365H[i]-(1-r/100))*0.9362)
      #resultado 1 eu perco 100% do meu capital
      else:
        resultado_favor.append(-100)

    #Criando um gráfico para ver os resultados
    ax_1[2,0].plot(pd.Series(resultado_favor).cumsum(),lw=2)
    ax_1[2,0].set_title(f"Back Strategy odds <= 1.6", fontsize=20)
    ax_1[2,0].legend(["Line 0","4%","6%","8%","10%"])
  for r in range(0,7,2):
    #Apostas lay com a bet
    resultado_contra=[]
    for i in range(len(round)):
      #se o resultado for 1 eu ganho 100% do capital investido
      if round.FTR[i]==1:
        resultado_contra.append(100*0.9362)
      #resultado 1 eu perco 100% da odd
      else:
        resultado_contra.append(-100*(round.B365H[i]-(1+r/100)))

    #Criando um gráfico para ver os resultados
    ax_1[2,1].axhline(y = 0 , color="red",linestyle = '-',alpha=0.6)
    ax_1[2,1].plot(pd.Series(resultado_contra).cumsum(),lw=2)
    ax_1[2,1].set_title(f"Lay Strategy odds <= 1.6", fontsize=20)
    ax_1[2,1].legend(["Line 0", "0%","2%","4%","6%"])

  fig3.tight_layout()
  fig3.savefig('fig3.png')

  return df,descritive, vo, opp
