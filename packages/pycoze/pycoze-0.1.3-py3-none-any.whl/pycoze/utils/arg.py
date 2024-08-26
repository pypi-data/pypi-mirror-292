import argparse


def read_arg(param: str, is_path=False):
    parser = argparse.ArgumentParser()
    parser.add_argument(param, nargs='?', help=f'Parameter {param}')
    args = parser.parse_args()
    value = getattr(args, param.lstrip('-'))
    # 如果是路径并且有引号，去掉引号
    if is_path and value and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]

    return value
