# coding=utf-8
import streamlit as st
import copy
from tronpy import Tron, Contract
from tronpy.keys import PrivateKey






#左侧

st.title("Tron网页轻钱包")
player = st.text_input('Tron钱包地址(address)')
tplayer=""

if len(player) > 30 :
    tplayer = player
    player=""
player=player.lower()

key = st.text_input('如果需要转账,请输入Tron私钥(key)',type="password")



option2 = st.sidebar.radio(
    "功能选项",
     ["Tron钱包","TRON钱包批量生成"])





def password(account_name):
    from beemgraphenebase.account import PasswordKey
    import random
    num = random.sample("stringascii_letters", 10)
    strs = ''
    password = strs.join(num)
    owner_key = PasswordKey(account_name, password, role="owner")
    owner_key=owner_key.get_private()
    key = "P5" + (str(owner_key))[2:51]
    return key


if option2 == "Tron钱包":
    @st.cache
    def trx_balance(client, tplayer):
        token = client.get_account_balance(tplayer)
        token_list = [{"TRX": float(token), "precision": 6, "id": 0},
                      {"列表内没有币种": "添加TRC20合约地址进行转账", "precision": 6, "id": 0}]
        token = client.get_account_asset_balances(tplayer)
        if len(token) != 0:
            for i in token:
                try:
                    tokenid = i
                    token_num = client.get_asset(tokenid)
                    # print(token_num)
                    token_name = token_num["abbr"]
                    try:
                        precision = token_num["precision"]
                    except:
                        precision = 0
                    token_balance = token[i] / (10 ** precision)
                    trc10 = {token_name: token_balance, "precision": precision,"id":tokenid}
                    print(trc10)
                    token_list.append(trc10)
                except:
                    pass
        return token_list

    def trans_trx(key,tplayer,to_add,to_num,memo):
        # trx转账
        client = Tron()
        priv_key = PrivateKey(bytes.fromhex(key))
        txn = (
            client.trx.transfer(tplayer, to_add, int(to_num * 1000000))
                .memo(memo)
                .build()
                .inspect()
                .sign(priv_key)
                .broadcast()
        )
        print(txn)
        # > {'result': True, 'txid': '5182b96bc0d74f416d6ba8e22380e5920d8627f8fb5ef5a6a11d4df030459132'}

        ok=txn.wait()
        return ok
    def trc10_trans(key,tplayer,to_add,to_num,token_ids,token_pre,memo):
        # trc10转账
        client = Tron()
        priv_key = PrivateKey(bytes.fromhex(key))

        txn = (
            client.trx.asset_transfer(
                tplayer, to_add, int(to_num * (10 ** token_pre)), token_id=token_ids
            )
                .memo(memo)
                .fee_limit(0)
                .build()
                .inspect()
                .sign(priv_key)
                .broadcast()
        )

        print(txn)
        ok = txn.wait()
        return ok


    @st.cache
    def trc20_balance_name(to_con,client):
        contract = client.get_contract(to_con)
        trc20_name = contract.functions.symbol()
        trc20_balance = contract.functions.balanceOf(tplayer)
        trc20_decimals = contract.functions.decimals()
        print(trc20_name, trc20_balance,trc20_decimals)
        return trc20_name, trc20_balance,trc20_decimals

    def trc2_trans(to_con,key,tplayer,to_add,to_num,trc20_decimals):
        client = Tron()
        contract = client.get_contract(to_con)
        priv_key = PrivateKey(bytes.fromhex(key))

        txn = (
            contract.functions.transfer(to_add, int(to_num * (10 ** trc20_decimals)))
                .with_owner(tplayer)
                .fee_limit(1_000_000)
                .build()
                .sign(priv_key)
                .inspect()
                .broadcast()
        )

        # wait
        ok = txn.wait()
        print("结果", ok)
        return ok


    st.progress(100)
    st.title("Tron钱包")
    client = Tron()

    token_list = [{"TRX": 0,"precision":6,"id":0}]
    token_list2 = [{"TRX": 0},{"列表内没有币种": "添加TRC20合约地址进行转账"}]
    if tplayer != "":
        token_list = trx_balance(client, tplayer)
        token_list2=copy.deepcopy(token_list)
        for i in token_list2:
            del i["precision"]
            del i["id"]

        #print(token_list)
    token_trx=st.selectbox("转账币种选择(TOKEN)",token_list2)
    to_con = ""
    trc20_decimals = 0
    try:
        token_name = tuple(token_trx.keys())[0]
        if token_name == "列表内没有币种":
            to_con=st.text_input("转账币种合约地址：")
            if to_con != "":
                trc20_name, trc20_balance, trc20_decimals = trc20_balance_name(to_con, client)
                st.write("币种(TOKEN)：",trc20_name,"余额(Balance)：", trc20_balance)

    except:
        pass
    to_add=st.text_input("接收地址(To)：")
    to_num=st.text_input("数量(Quantity):")
    try:
        to_num=float(to_num)
    except:
        to_num=""
    tron_go=st.button("确定转账(ok)")


    if tron_go:
        if tplayer == "" or key=="" :
            st.write("请输入钱包地址或私钥")
        elif to_add =="" or to_num == "":
            st.write("请输入接收地址和数量")
        else:
            st.write("开始转账(go)")


            token_name=tuple(token_trx.keys())[0]
            if token_name =="列表内没有币种":
                st.write("TRC20转账")
                if to_con == "":
                    print("请输入币种合约地址")
                    st.write("请输入币种合约地址")
                else:
                    st.write("转账币种", trc20_name, "数量:", to_num)
                    trc20_name, trc20_balance, trc20_decimals = trc20_balance_name(to_con, client)
                    ok = trc2_trans(to_con, key, tplayer, to_add, to_num, trc20_decimals)
                    st.write("转账完成")
                    url = "https://tronscan.io/#/transaction/%s" % ok["id"]
                    st.write("区块信息：", url)
                    st.write("详细信息:", ok)

            else:
                token_pre=0
                token_ids=0
                for i in token_list:
                    name = tuple(i.keys())[0]
                    if name == token_name:
                        token_pre = i["precision"]
                        token_ids = i["id"]
                st.write("转账币种", token_name,"数量:",to_num)

                if token_name == "TRX":
                    memo=""
                    ok = trans_trx(key, tplayer, to_add, to_num, memo)
                    st.write("转账完成")
                    url="https://tronscan.io/#/transaction/%s" % ok["id"]
                    st.write("区块信息：",url)
                    st.write("详细信息:",ok)
                else:
                    st.write("TRC10转账")
                    memo=""
                    ok = trc10_trans(key, tplayer, to_add, to_num, token_ids, token_pre, memo)
                    st.write("转账完成")
                    url = "https://tronscan.io/#/transaction/%s" % ok["id"]
                    st.write("区块信息：", url)
                    st.write("详细信息:", ok)





if option2 == "TRON钱包批量生成":
    st.progress(100)
    st.title("TRON钱包批量生成")
    howmany=st.text_input("生成多少个钱包？(How many?)")
    howmany_button = st.button("确定生成(ok)")
    if howmany_button:
        try:
            howmany=int(howmany)
        except:
            howmany=1
        for i in range(howmany):
            priv_key = PrivateKey.random()
            print(priv_key)
            add = priv_key.public_key.to_base58check_address()
            print(add)

            st.write(i+1,"私钥:",priv_key)
            st.write(i + 1, "地址:", add)




