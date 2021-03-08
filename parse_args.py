from sys import argv
argc = int(len(argv))


def get_arguments(command_str):
    result_str = ''
    work = str(command_str)
    is_space = True
    while True:
        if len(work) < 1:
            break
        else:
            if work[0] == ' ':
                work = work[1:]
            else:
                break
    can_pass_space = False
    for i in range(len(work)):
        if work[i] == '\"':
            if can_pass_space:
                can_pass_space = False
            else:
                can_pass_space=True
                result_str += '\n'
        elif work[i] == ' ':
            if can_pass_space:
                result_str += ' '
            else:
                result_str += '\n'
        else:
            result_str += work[i]
    result=[]
    for i in result_str.split('\n'):
        if not i == '':
            result.append(i)
    return result


def set_arguments(args_mas):
    result = ''
    for i in args_mas:
        if not result == '':
            result += ' '
        result += '\"' + str(i) + '\"'
    return result