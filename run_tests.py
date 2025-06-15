#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化运行 client/test 下所有测试用例（assemble、fronted、backend），
采用 python -m 模块方式调用，
在终端显示进度条、当前阶段与文件名，并同步输出到日志文件。
"""
import os
import sys
import glob
import subprocess
import datetime

# 尝试引入 tqdm 进度条库
try:
    from tqdm import tqdm
    use_tqdm = True
except ImportError:
    use_tqdm = False


def file_to_module(root, filepath):
    # 将文件路径转为模块路径，比如 client/test/backend/foo.py -> client.test.backend.foo
    rel = os.path.relpath(filepath, root)
    mod = rel.replace(os.path.sep, '.')
    if mod.endswith('.py'):
        mod = mod[:-3]
    return mod


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    # 根目录
    root = os.path.dirname(os.path.abspath(__file__))
    test_root = os.path.join(root, 'client', 'test')
    log_dir = os.path.join(test_root, 'log')
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'test_run_{timestamp}.log')

    stages = ['assemble', 'fronted', 'backend']
    test_files = []
    for stage in stages:
        pattern = os.path.join(test_root, stage, '*.py')
        for f in sorted(glob.glob(pattern)):
            test_files.append((stage, f))

    total = len(test_files)
    if total == 0:
        print('未找到任何测试文件。请检查 client/test 下各目录。')
        sys.exit(1)

    bar = tqdm(total=total, unit='file', desc='Running tests', ncols=80) if use_tqdm else None

    print(f"共找到 {total} 个测试文件，日志记录到 {log_file}\n")
    with open(log_file, 'w', encoding='utf-8') as logf:
        for stage, filepath in test_files:
            module = file_to_module(root, filepath)
            header = f'[{stage}] Running module {module}'
            print(header)
            logf.write(header + '\n')
            logf.flush()

            # 调用 python -m <module>
            cmd = [sys.executable, '-m', module]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            # 实时输出并写日志
            for line in proc.stdout:
                print(line, end='')
                logf.write(line)
                logf.flush()
            proc.wait()

            if bar:
                bar.update(1)

        if bar:
            bar.close()

    print(f"\n测试完成，日志保存至: {log_file}")


if __name__ == '__main__':
    main()
