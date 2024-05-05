import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import json
import pandas as pd
import plotly.express as px   
import psycopg2 
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="PhonePe Data visualization", page_icon=":anchor:", layout="wide", menu_items=None)
phone=Image.open('phonepe.png')
select= option_menu(menu_title=None,
                    options = ["Home","Explore Data","Overall Analysis"],
                    default_index=0,
                    orientation="horizontal",
                    styles={
            "container": {"padding": "0!important", "background-color": "white","size":"cover"},
            "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#6F36AD"},
            "nav-link-selected": {"background-color": "#6F36AD"}
        } )
if select == "Home":
    st.title(':violet[PhonePe Data Visualization]')

    col1,col2 = st.columns(2)
    with col1:
        st.image(phone, width=200)
    phonepe_description = """PhonePe has launched PhonePe Pulse, a data analytics platform that provides insights into
                        how Indians are using digital payments. With over 30 crore registered users and 2000 crore 
                        transactions, PhonePe, India's largest digital payments platform with 46% UPI market share,
                        has a unique ring-side view into the Indian digital payments story. Through this app, you 
                        can now easily access and visualize the data provided by PhonePe Pulse, gaining deep 
                        insights and interesting trends into how India transacts with digital payments."""
    phonepe="""
            The Indian digital payments story has truly captured the world's imagination. 
            From the largest towns to the remotest villages, there is a payments revolution being driven by the penetration of mobile phones, 
            mobile internet and state-of-the-art payments infrastructure built as Public Goods championed by the central bank and the government. Founded in December 2015, 
            PhonePe has been a strong beneficiary of the API driven digitisation of payments in India. 
            When we started, we were constantly looking for granular and definitive data sources on digital payments in India. PhonePe Pulse is our way of giving back to the digital payments ecosystem."""
    st.write(phonepe_description)
    st.write(phonepe)

mydb=psycopg2.connect(host="localhost",
                        user="postgres",
                        password="root",
                        database="phonepe",
                        port="5432")
mycursor=mydb.cursor()
mycursor.execute("select* from aggregated_transaction")
agg_t=pd.DataFrame(mycursor.fetchall(),columns=("States", "Years", "Quarter", "Transaction_type","Transaction_count", "Transaction_amount"))

mycursor.execute("select* from aggregated_user")
agg_u=pd.DataFrame(mycursor.fetchall(),columns=("States", "Years", "Quarter", "Brand", "Registered_User", "User_Percentage"))

mycursor.execute("select* from map_transactions")
map_t=pd.DataFrame(mycursor.fetchall(),columns=("States","District", "Years", "Quarter","Transaction_count", "Transaction_amount"))

mycursor.execute("select* from map_user")
map_u=pd.DataFrame(mycursor.fetchall(),columns=("States","District", "Years", "Quarter","Registered_user", "AppOpened"))

mycursor.execute('select * from top_transaction_district')
top_t_d=pd.DataFrame(mycursor.fetchall(),columns=("States","District", "Years", "Quarter","Transaction_count", "Transaction_amount"))

mycursor.execute('select * from top_transaction_pincode')
top_t_p=pd.DataFrame(mycursor.fetchall(),columns=("States","Pincode", "Years", "Quarter","Transaction_count", "Transaction_amount"))

mycursor.execute("select* from top_user_district")
top_u_d=pd.DataFrame(mycursor.fetchall(),columns=("States","District", "Years", "Quarter","Registered_user"))

mycursor.execute("select* from top_user_pincode")
top_u_p=pd.DataFrame(mycursor.fetchall(),columns=("States","Pincode", "Years", "Quarter","Registered_user"))


url_map="https://raw.githubusercontent.com/pnraj/Projects/master/Phonephe_Pulse/data/states_india.geojson"


def agg_trans_amt(df,year,quarter):
    tot_count= df[(df["Years"]== year) & (df["Quarter"] == quarter)]
    tot_count_s=tot_count.groupby("States")[["Transaction_amount","Transaction_count"]].sum()
    tot_count_s.reset_index(inplace=True)
    

    tot_count_s1=tot_count.groupby("Transaction_type")[["Transaction_amount"]].sum()
    tot_count_s1.reset_index(inplace=True)
    blankIndex=[''] * len(tot_count_s1)
    tot_count_s1.index=blankIndex
    t=round(tot_count_s1.nlargest(10,["Transaction_amount"]))


    Total_Transaction=round(tot_count["Transaction_amount"].sum())
    Total_count=round(tot_count["Transaction_count"].sum())
    Avg_Trans_value=round(Total_Transaction/Total_count)

    c1,c2=st.columns([2,1])
    with c2:
        st.write("")
        st.write("")
        st.write('##### :violet[All PhonePe transactions (UPI + Cards + Wallets)]')
        st.write(f'#### {Total_count}')
        st.write('##### :violet[Total payment value]')
        st.write(f'#### {Total_Transaction}')
        st.write('##### :violet[Avg. transaction value]')
        st.write(f'#### {Avg_Trans_value}')
        st.write('### :violet[Categories]')
        st.dataframe(t,width=400)
        
    with c1:
        #st.plotly_chart(chart_amt)
        response = requests.get(url_map)
        map1=json.loads(response.content)
        states_name= []
        for feature in map1["features"]:
            states_name.append(feature["properties"]['st_nm'])
        states_name.sort()

        map_india_1= px.choropleth(tot_count_s, geojson= map1, 
                                        locations= "States", 
                                        featureidkey= "properties.st_nm",
                                        color= "Transaction_amount", 
                                        color_continuous_scale= "twilight",
                                        range_color= (tot_count_s["Transaction_amount"].min(), 
                                                    tot_count_s["Transaction_amount"].max()),
                                        hover_name= "States", 
                                        title= f"{year} Quarter {quarter} TRANSACTION AMOUNT all over INDIA", 
                                        fitbounds= "locations",
                                        height= 600,width=800)
        map_india_1.update_geos(visible= False)
        st.plotly_chart(map_india_1)


    
def map_trans_s(df,year,quarter):
    map_tran=df[(df["Years"] == year) & (df["Quarter"]== quarter)]
    map_tran_s1 = map_tran.groupby("States")[["Transaction_amount"]].sum()
    map_tran_s1.reset_index(inplace=True)
    m_top_10 = round(map_tran_s1.nlargest(10, ["Transaction_amount"]))
    #top_10.sort_values(by=["Transaction_amount"], ascending=False, inplace=True)
    blankIndex=[''] * len(m_top_10)
    m_top_10.index=blankIndex
    chart1= px.bar(m_top_10, x='States',y='Transaction_amount',title=f'Top 10 States by Transaction_amount in {year} Q{quarter}',
         color_discrete_sequence=px.colors.sequential.Viridis,height=400,width=800)
    c1,c2=st.columns([1,2])
    with c1:
        st.write("#### :violet[Sub_Categories]")
        st.dataframe(m_top_10,width=400)
    with c2:
        st.plotly_chart(chart1)



def map_trans_d(df,year,quarter):
    map_tran=df[(df["Years"] == year) & (df["Quarter"]== quarter)]
    map_tran_s= round(map_tran.groupby("District")[["Transaction_amount"]].sum())
    map_tran_s.reset_index(inplace=True)
    blankIndex=[''] * len(map_tran_s)
    map_tran_s.index=blankIndex

    top_10=map_tran_s.nlargest(10,["Transaction_amount"])
    top_10.sort_values(by=["Transaction_amount"], ascending=True, inplace=True)
    chart2= px.bar(top_10, y='District',x='Transaction_amount',title=f'Top 10 District by Transaction_amount in {year} Q{quarter}',
        orientation='h',
        color_discrete_sequence=px.colors.sequential.Greens_r,height=500,width=800)

    c1,c2=st.columns([1,2])
    with c1:
        st.write("#### :violet[Sub_Categories]")
        st.dataframe(top_10,width=400)
    with c2:
        st.plotly_chart(chart2)

def top_trans_pin(df,year,quarter):
    top_tp=df[(df["Years"] == year) & (df["Quarter"] == quarter)]
    top_tp_s = round(top_tp.groupby("Pincode")[["Transaction_amount"]].sum())
    top_tp_s.reset_index(inplace=True)
    blankIndex=[''] * len(top_tp_s)
    top_tp_s.index=blankIndex
    tp_top_10=top_tp_s.nlargest(10,["Transaction_amount"])

    chart3= px.pie(tp_top_10, names='Pincode',values='Transaction_amount',title=f'Top 10 Pincode by Transaction_amount in {year} Q{quarter}',
         color_discrete_sequence=px.colors.sequential.Viridis,height=500,width=800,hole=0.5)
    c1,c2=st.columns([1,2])
    with c1:
        st.write("#### :violet[Sub_Categories]")
        st.dataframe(tp_top_10,width=400)
    with c2:
        st.plotly_chart(chart3)


def map_user1(df, year, quarter):
    map_user = df[(df["Years"] == year) & (df["Quarter"] == quarter)]
    tot_registered = map_user["Registered_user"].sum()
    tot_app_opened= map_user["AppOpened"].sum()

    tot_user_s1=map_user.groupby("States")[["Registered_user"]].sum()
    tot_user_s1.reset_index(inplace=True)
    

    c1,c2=st.columns([5,1])
    with c2:
        st.write("")
        st.write("")
        st.write("")
        st.write("### :violet[Users]")
        st.write("")
        st.write('#### :violet[Registered PhonePe users]')
        st.write(f'#### {tot_registered}')
        st.write('#### :violet[PhonePe AppOpened]')
        st.write(f'#### {tot_app_opened}')

    with c1:
        response = requests.get(url_map)
        map1=json.loads(response.content)
        states_name= []
        for feature in map1["features"]:
            states_name.append(feature["properties"]['st_nm'])
        states_name.sort()

        map_india_2= px.choropleth(tot_user_s1, geojson= map1, locations= "States", featureidkey= "properties.st_nm",
                                color= "Registered_user", color_continuous_scale= "twilight",
                                range_color= (tot_user_s1["Registered_user"].min(), tot_user_s1["Registered_user"].max()),
                                hover_name= "States", title= f"{year} Quarter {quarter} Registered Users all over INDIA", fitbounds= "locations",
                                height= 600,width= 1000)
        map_india_2.update_geos(visible= False)

        st.plotly_chart(map_india_2)

def agg_user(df,year,quarter):
    tot_user=df[(df["Years"]== year) & (agg_u["Quarter"]== quarter)]
    tot_user_s1=tot_user.groupby("States")[["Registered_User"]].sum()
    tot_user_s1.reset_index(inplace=True)
    s_top_10=tot_user_s1.nlargest(10,["Registered_User"])
    blankIndex=[''] * len(s_top_10)
    s_top_10.index=blankIndex
    chart4= px.bar(s_top_10, x='States',y='Registered_User',title=f'Top 10 States by Registered Users in {year} Q{quarter}',
         color_discrete_sequence=px.colors.sequential.Viridis,height=400,width=800)
    c1,c2=st.columns([1,2])
    with c1:
        st.write("#### :violet[Sub_Categories]")
        st.dataframe(s_top_10,width=600)
    with c2:
        st.plotly_chart(chart4)

    
    

def top_user_pin(df,year,quarter):
    top_up=df[(df["Years"] == year) & (df["Quarter"] == quarter)]
    top_up_s =top_up.groupby("Pincode")[["Registered_user"]].sum()
    top_up_s.reset_index(inplace=True)
    blankIndex=[''] * len(top_up_s)
    top_up_s.index=blankIndex
    up_top_10=top_up_s.nlargest(10,["Registered_user"])
    chart5= px.pie(up_top_10, names='Pincode',values='Registered_user',title=f'Top 10 Pincode by Registered user in {year} Q{quarter}',
         color_discrete_sequence=px.colors.sequential.Viridis,height=500,width=800,hole=0.5)
    c1,c2=st.columns([1,2])
    with c1:
        st.write("##### :violet[Sub Categories]")
        st.dataframe(up_top_10,width=400)
    with c2:
        st.plotly_chart(chart5)

    

def top_user_dist(df,year,quarter):
    top_ud=df[(df["Years"] == year) & (df["Quarter"] == quarter)]
    top_ud_s =top_ud.groupby("District")[["Registered_user"]].sum()
    top_ud_s.reset_index(inplace=True)
    blankIndex=[''] * len(top_ud_s)
    top_ud_s.index=blankIndex
    ud_top_10=top_ud_s.nlargest(10,["Registered_user"])
    ud_top_10.sort_values(by=["Registered_user"], ascending=True, inplace=True)
    chart6= px.bar(ud_top_10, y='District',x='Registered_user',title=f'Top 10 District by Registered user in {year} Q{quarter}',
        orientation='h',
        color_discrete_sequence=px.colors.sequential.Greens_r,height=500,width=800)
    c1,c2=st.columns([1,2])
    with c1:
        st.write("##### :violet[Sub Categories]")
        st.dataframe(ud_top_10,width=400)
    with c2:
        st.plotly_chart(chart6)

def states(df,year,quarter,state):
    a=df[ (df["Years"] == year) & (df["Quarter"] == quarter) & (df["States"] == state) ]
    Total_Transaction1=round(a["Transaction_amount"].sum())
    Total_count1=round(a["Transaction_count"].sum())
    Avg_Trans_value1=round(Total_Transaction1/Total_count1)

    cha1= round(a.groupby("District")[["Transaction_amount"]].sum())
    cha1.reset_index(inplace=True)
    chart5= px.line(cha1, x='District',y='Transaction_amount',title=f'Transaction_amount in {state} District-wise({year} Q{quarter})',
        color_discrete_sequence=px.colors.sequential.Viridis,height=500,width=800,markers=True)

    s1,s2 = st.columns([1,2])
    with s1:
        st.write("")
        st.write("")
        st.write("")
        st.write('##### :violet[Total Transactions]')
        st.write(f'#### {Total_count1}')
        st.write('##### :violet[Total payment value]')
        st.write(f'#### {Total_Transaction1}')
        st.write('##### :violet[Avg transaction value]')
        st.write(f'#### {Avg_Trans_value1}')
    with s2:
        st.plotly_chart(chart5)
    
def states1(df,year,quarter,state):
    map_user1 = df[(df["Years"] == year) & (df["Quarter"] == quarter) & (df["States"] == state)]
    tot_registered1 = map_user1["Registered_user"].sum()
    tot_app_opened1 = map_user1["AppOpened"].sum()

    cha2= round(map_user1.groupby("District")[["Registered_user"]].sum())
    cha2.reset_index(inplace=True)
    chart6= px.line(cha2, x='District',y="Registered_user",title=f'Registered user in {state} District-wise({year} Q{quarter})',
            color_discrete_sequence=px.colors.sequential.Viridis,height=500,width=800,markers=True)
    
    s1,s2 = st.columns([1,2])
    with s1:
        st.write("")
        st.write("")
        st.write("")
        st.write('##### :violet[Registered users]')
        st.write(f'#### {tot_registered1}')
        st.write('##### :violet[AppOpened]')
        st.write(f'#### {tot_app_opened1}')
        
    with s2:
        st.plotly_chart(chart6)


if select == 'Explore Data':
    c1,c2,c3=st.columns(3)
    with c1:
        options = ["Users", "Transactions"]
        default_index = options.index("Transactions")
        u_t = st.selectbox("Payemnts", options,key='u_t',index=default_index)
    if u_t == "Transactions":
        with c2:
            years=st.selectbox("Select the Year",agg_t["Years"].unique(),key="years")
        with c3:
            qua=st.selectbox("Select the Quarters",agg_t["Quarter"].unique(),key="qua")
        agg_trans_amt(agg_t, years, qua)

        
        options1 = ["State","District", "Pincode"]
        default_index = options1.index("State")
        tran = st.radio("Select Sub Categories", options1 ,key='tran',index=default_index,horizontal=True)
        if tran== "State":
            map_trans_s(map_t,years,qua)
        elif tran== "District":
            map_trans_d(map_t,years,qua)
        else:
            top_trans_pin(top_t_p,years,qua)

        
        state= st.selectbox("Select the State",map_t["States"].unique(),key="state")

        states(map_t,years,qua,state)

        
    else:
        with c2:
            u_year=st.selectbox("Select the Year",agg_u["Years"].unique(),key="u_year")
        with c3:
            u_qua=st.selectbox("Select the Quarters",agg_u["Quarter"].unique(),key="u_qua")

        map_user1(map_u,u_year,u_qua)

        
        options2 = ["State","District", "Pincode"]
        default_index = options2.index("State")
        user = st.radio("Select Sub Categories", options2 ,key='tran',index=default_index,horizontal=True)

        if user== "State":
            agg_user(agg_u,u_year,u_qua)
        elif user== "District":
            top_user_dist(top_u_d,u_year,u_qua)
        else:
            top_user_pin(top_u_p,u_year,u_qua)

        state1= st.selectbox("Select the State",map_u["States"].unique(),key="state")

        states1(map_u,u_year,u_qua,state1)


if select == "Overall Analysis":
    quest = st.selectbox("Select Questions for analyis",
        ["Click the question that you would like to analyse",
        "1. Top 10 States with heighest Transaction amount",
        "2. Top 10 States with heighest Registered Users",
        "3. Top 10 Mobile brands with heighest Registrations",
        "4. Transaction done over all these years",
        "5. Top 10 District with heighest Transaction amount",
        "6. Top 10 pincode with heighest Transaction amount",
        "7. Total Transaction each year",
        "8. Registered User each year",
        "9. State that performed well every year"])
    
    if quest== "1. Top 10 States with heighest Transaction amount":
        mycursor.execute('''select "State",round(sum("Transaction_amount")::numeric,0) as Transaction_amount from map_transactions group by "State"
                    order by sum("Transaction_amount") desc
                    Limit 10''')
        one=pd.DataFrame(mycursor.fetchall(),columns=(["State","Transaction_amount"]))

        que1= px.bar(one, x='State',y='Transaction_amount',
        color_discrete_sequence=px.colors.sequential.RdBu_r)

        q1,q11=st.columns([1,2])
        with q1:
            st.dataframe(one)
        with q11:
            st.plotly_chart(que1)




    elif quest== "2. Top 10 States with heighest Registered Users":
        mycursor.execute('''select "State",sum("Registered_user") as Registered_user, sum("Appopened") as Appopened from map_user
        group by "State"
        order by sum("Registered_user") desc
        Limit 10''')
        two=pd.DataFrame(mycursor.fetchall(),columns=(["States","Registered_user","Appopened"]))

        t1=go.Bar(x=two["States"], y=two["Registered_user"], name="Registered_user")
        t2=go.Bar(x=two["States"], y=two["Appopened"], name="Appopened")

        que2=go.Figure(data=[t1,t2],layout=go.Layout(barmode="group"))
        
        q2,q12=st.columns([1,2])
        with q2:
            st.dataframe(two)
        with q12:
            st.plotly_chart(que2)


    elif quest == "3. Top 10 Mobile brands with heighest Registrations":
        mycursor.execute('''select "Brand",sum("User_count") from aggregated_user
        group by "Brand"
        order by sum("User_count") desc
        Limit 10''')
        three=pd.DataFrame(mycursor.fetchall(),columns=(["States","User_Count"]))

        que3= px.bar(three, y='States',x="User_Count",orientation="h",
        color_discrete_sequence=px.colors.sequential.haline)


        q2,q12=st.columns([1,2])
        with q2:
            st.dataframe(three)
        with q12:
            st.plotly_chart(que3)

    elif quest== "4. Transaction done over all these years":
        mycursor.execute('''select "Transaction_type",round(sum("Transaction_amount")::numeric,0) from aggregated_Transaction
        group by "Transaction_type"
        order by sum("Transaction_amount") desc''')
        four=pd.DataFrame(mycursor.fetchall(),columns=(["Transaction_type","Transaction_amount"]))

        que4= px.line(four, x='Transaction_type',y="Transaction_amount",markers=True,
        color_discrete_sequence=px.colors.sequential.PuBuGn_r)


        q2,q12=st.columns([1,2])
        with q2:
            st.dataframe(four)
        with q12:
            st.plotly_chart(que4)

    

    elif quest == "5. Top 10 District with heighest Transaction amount":
        mycursor.execute('''select "State","District",round(sum("Transaction_amount")::numeric,0) from map_transactions
        group by "District","State"
        order by sum("Transaction_amount") desc
        limit 10''')
        five=pd.DataFrame(mycursor.fetchall(),columns=(["State","District","Transaction_amount"]))
        que5= px.line(five, x='District',y="Transaction_amount",markers=True,hover_name='State',
        color_discrete_sequence=px.colors.sequential.Jet_r)

        q2,q12=st.columns([1,2])
        with q2:
            st.dataframe(five)
        with q12:
            st.plotly_chart(que5)
        

    elif quest == "6. Top 10 pincode with heighest Transaction amount":
        mycursor.execute('''select "State","District",round(sum("Transaction_amount")::numeric,0) from top_transaction_pincode
        group by "District","State"
        order by sum("Transaction_amount") desc
        limit 10''')
        six=pd.DataFrame(mycursor.fetchall(),columns=(["State","Pincode","Transaction_amount"]))

        que6= px.pie(six, names='Pincode',values="Transaction_amount",hover_name='State',
        color_discrete_sequence=px.colors.sequential.Greens_r,hole=0.5)

        q2,q12=st.columns([1,2])
        with q2:
            st.dataframe(six)
        with q12:
            st.plotly_chart(que6)
        

    elif quest == "7. Total Transaction each year":
        mycursor.execute('''select "Year",round(sum("Transaction_amount")::numeric,0) from map_transactions 
        group by "Year"
        order by sum("Transaction_amount")''')
        seven=pd.DataFrame(mycursor.fetchall(),columns=(["Year","Transaction_amount"]))

        seven["Year"] = seven["Year"].astype(str)
        que7= px.bar(seven, x='Year',y="Transaction_amount",
        color_discrete_sequence=px.colors.sequential.haline)

        q2,q12=st.columns([1,2])
        with q2:
            st.dataframe(seven)
        with q12:
            st.plotly_chart(que7)
        
        

    elif quest =="8. Registered User each year":
        mycursor.execute('''select "Year",sum("Registered_user") from map_user
        group by "Year"
        order by sum("Registered_user")''')
        eight=pd.DataFrame(mycursor.fetchall(),columns=(["Year","Registered_user"]))

        eight["Year"] = eight["Year"].astype(str)
        que8= px.pie(eight, names='Year', values="Registered_user",
        color_discrete_sequence=px.colors.sequential.Peach_r)

        q2,q12=st.columns([1,2])
        with q2:
            st.dataframe(eight)
        with q12:
            st.plotly_chart(que8)
        

    elif quest == "9. State that performed well every year":
        mycursor.execute('''SELECT mt."Year", mt."State", round(MAX(mt."Transaction_amount")::numeric,0) AS max_transaction
        FROM map_transactions mt
        JOIN (
            SELECT "Year", MAX("Transaction_amount") AS max_amount
            FROM map_transactions
            GROUP BY "Year"
        ) max_per_year 
        ON mt."Year" = max_per_year."Year" AND mt."Transaction_amount"= max_per_year.max_amount
        GROUP BY mt."Year", mt."State" ''')
        nine=pd.DataFrame(mycursor.fetchall(),columns=(["Year","State","Transaction_amount"]))

        nine["Year"] = nine["Year"].astype(str)

        que9= px.bar(nine, x='Year', y="Transaction_amount",hover_name="State",
        color_discrete_sequence=px.colors.sequential.Magenta_r)

        q2,q12=st.columns([1,2])
        with q2:
            st.dataframe(nine)
        with q12:
            st.plotly_chart(que9)
        


    








   

    