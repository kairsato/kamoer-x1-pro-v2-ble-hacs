import struct,datetime
d=open("btsnoop_hci.log.last",'rb').read()
o=16;n=0;pk=[]
while o+24<=len(d):
    orig,incl,flags,drops,ts=struct.unpack('>IIIIq',d[o:o+24]);o+=24
    p=d[o:o+incl];o+=incl;n+=1
    t=datetime.datetime(1,1,1)+datetime.timedelta(microseconds=ts-0x00E03AB44A676000+0x00dcddb30000000-0x00dcddb30000000) if False else datetime.datetime(1970,1,1)+datetime.timedelta(microseconds=ts-0x00dcddb30f2f8000)
    pk.append((n,flags,t,p))
print(pk[0][2],pk[-1][2])
# connection events
for n,fl,t,p in pk:
    if p[0]==4 and p[1]==0x3e and p[3] in (1,0xa):
        sub=p[3];h=struct.unpack('<H',p[5:7])[0]; a=p[8:14][::-1].hex(':')
        print(n,t.time(),"LE conn",hex(sub),"handle",h&0xfff,"addr",a)
    if p[0]==4 and p[1]==5: print(n,t.time(),"disconn",struct.unpack('<H',p[4:6])[0],"reason",hex(p[6]))
print("=== addr fix")
for n,fl,t,p in pk:
    if p[0]==4 and p[1]==0x3e and p[3] in (1,0xa):
        print(n,t.time(),"handle",struct.unpack('<H',p[4+1+0:4+1+2] if False else p[5:7])[0]&0xfff,"st",p[4],"role",p[7],"atype",p[8],"addr",p[9:15][::-1].hex(':'))
ops={0x01:'ErrRsp',0x02:'MtuReq',0x03:'MtuRsp',0x04:'FindInfoReq',0x05:'FindInfoRsp',0x06:'FindByTypeReq',0x07:'FindByTypeRsp',0x08:'ReadByTypeReq',0x09:'ReadByTypeRsp',0x0a:'ReadReq',0x0b:'ReadRsp',0x10:'ReadByGroupReq',0x11:'ReadByGroupRsp',0x12:'WriteReq',0x13:'WriteRsp',0x52:'WriteCmd',0x1b:'Notify',0x1d:'Indicate',0x1e:'Confirm'}
print("=== ATT handle 66")
for n,fl,t,p in pk:
    if p[0]==2:
        h=struct.unpack('<H',p[1:3])[0]&0xfff
        if h==66 and len(p)>9:
            cid=struct.unpack('<H',p[7:9])[0]
            dirn='TX' if fl&1==0 else 'RX'
            print(n,t.time(),dirn,"cid",cid,ops.get(p[9],hex(p[9])) if cid==4 else '',p[9:].hex()[:120])
