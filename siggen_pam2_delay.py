#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script generates a pwl waveform file.
"""

def de_bruijn(k, n):
    """
    De Bruijn sequence for alphabet k
    and subsequences of length n.
    """
    a = [0] * k * n
    sequence = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                sequence.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)
    db(1, 1)

    return sequence + sequence[:n]


def format_neg(vec):
    if vec[0][0] >= 0.0:
        return vec
    for i in range(len(vec)):
        cx, cy = vec[i]
        if cx == 0.0:
            return vec[i:]
        elif cx > 0.0:
            px, py = vec[i - 1]
            zy = (0.0 - px) / (cx - px) * cy + (cx - 0.0) / (cx - px) * py
            return [(0.0, zy)] + vec[i:]


# def code_to_voltage(code, amp):
#     return (code - 1.5) / 1.5 * amp
def code_to_value(code, type):
    if type == 'current':
        return '\'ileak\'' if code == 0 else '\'ihold\''
    elif type == 'voltage':
        return 0 if code == 0 else '\'xvcc\''

def get_time_value_pairs(pattern, tbit, tinterval, td=0, tr=10e-9):
    td_s = 2e-9
    iinit = 0
    vinit = 0
    tcur = td
    if tcur >= 0.0:
        data_pwl = [(0.0, iinit)]
        signal_pwl = [(0.0, vinit)]
    else:
        data_pwl = [(tcur - td_s, iinit)]
        signal_pwl = [(tcur, vinit)]

    if tcur > 0.0:
        print('{}'.format(tcur-td_s))
        data_pwl.append((tcur - td_s, iinit))
        signal_pwl.append((tcur, vinit))
        
    for idx, code in enumerate(pattern):
        icur = code_to_value(code, 'current')
        vhi = code_to_value(1, 'voltage')
        vlo = code_to_value(0, 'voltage')
        # vcur = code_to_value(code, 'voltage')
        # inxt = icur if idx == len(pattern) - 1 else code_to_value(pattern[idx + 1], 'current')
        # vnxt = vcur if idx == len(pattern) - 1 else code_to_value(pattern[idx + 1], 'voltage')
        data_pwl.append((tcur - td_s + tr, icur))
        data_pwl.append((tcur + td_s + tr + tbit, icur))
        data_pwl.append((tcur + td_s + tr*2 + tbit, 0))
        data_pwl.append((tcur - td_s + tr*2 + tbit + tinterval, 0))
        signal_pwl.append((tcur + tr, vhi))
        signal_pwl.append((tcur + tr + tbit, vhi))
        signal_pwl.append((tcur + tr*2 + tbit, vlo))
        signal_pwl.append((tcur + tr*2 + tbit + tinterval, vlo))
        tcur += tr*2 + tbit + tinterval

    return format_neg(data_pwl), format_neg(signal_pwl)

if __name__ == '__main__':
    nsym = 2
    nlen = 3
    data = de_bruijn(nsym, nlen)
    data = data + data[:2 * nlen]
    print(data)
    tbit = 10e-9
    tinterval = 55e-9
    tdelay = 5e-9
    tr = 300e-12
    data_pwl = './data_pwl_{}_{}_{}_{}.txt'.format(nsym, nlen, tbit, tinterval)
    switch_pwl = './switch_pwl_{}_{}_{}_{}.txt'.format(nsym, nlen, tbit, tinterval)
    data_out, signal_out = get_time_value_pairs(data, tbit, tinterval, td=tdelay, tr=tr)

    with open(data_pwl, 'w') as f:
        for t, v in data_out:
            f.write('{:.6g} {}\n'.format(t, v))
        print('last time = %.4g' % t)

    with open(switch_pwl, 'w') as f:
        for t, v in signal_out:
            f.write('{:.6g} {}\n'.format(t, v))
        print('last time = %.4g' % t)
