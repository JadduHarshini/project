from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
def atoken(email,seconds):
    s=Serializer('*#$harshaaaa',seconds)
    return s.dumps({'user':email}).decode('utf-8')
