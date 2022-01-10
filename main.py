import os
import typing as tp
import libtmux
import pathlib
import argparse
import getpass
from tqdm import tqdm
import logging
import shutil

# logger = logging.getLogger('TmuxJupyterSession')
logging.basicConfig(level=logging.INFO)


class TmuxJupyterSession:
    FOLDER_NAME = 'tmux_jupyter_folder'
    WINDOW_NAME = 'tmux_window'
    SESSION_DEFAULT_NAME = str(getpass.getuser()) + 'tmux_session'

    def __init__(self):

        self.created_dir = []

    def start(self,
              num_users: int,
              base_dir: str = './',
              ip: str = '0.0.0.0',
              ports: tp.List[int] = None,
              session_name: str = SESSION_DEFAULT_NAME):
        """
        Запустить $num_users ноутбуков. У каждого рабоча ` директория $base_dir + $folder_num
        """

        if base_dir != './':
            pathlib.Path(base_dir).mkdir(parents=True, exist_ok=True)

        ports = ports if ports else list(range(11212, 11212 + num_users))
        server = libtmux.Server()

        session = server.find_where({"session_name": session_name}) if server.has_session(session_name) \
            else server.new_session(session_name, start_directory=base_dir)

        max_existing_number_in_folder = 1
        for filename in os.listdir():
            if len(filename) > len(self.FOLDER_NAME) and filename[:len(self.FOLDER_NAME)] == self.FOLDER_NAME:
                max_existing_number_in_folder = max(max_existing_number_in_folder,
                                                    int(filename[len(self.FOLDER_NAME):]))

        for _, port in tqdm(zip(range(1, num_users + 1), ports), total=num_users):
            max_existing_number_in_folder += 1
            new_dir = f'{base_dir}{self.FOLDER_NAME}{max_existing_number_in_folder}'
            logging.info(new_dir)

            pathlib.Path(new_dir).mkdir(parents=True, exist_ok=True)
            self.created_dir.append(new_dir)

            window = session.new_window(window_name=f'{self.WINDOW_NAME}{max_existing_number_in_folder}',
                                        start_directory=new_dir,
                                        attach=True)

            new_dir_name = new_dir[2:]
            logging.info(f"{os.getcwd()}/{new_dir_name}")
            window.attached_pane.send_keys(f'jupyter notebook --ip {ip} --port {port} --no-browser '
                                           f'--NotebookApp.notebook_dir="{os.getcwd()}/{new_dir_name}" ')


            import time
            time.sleep(1)

    def stop(self, num, session_name=SESSION_DEFAULT_NAME):
        """
        @:param session_name: Названия tmux-сессии, в которой запущены окружения
        @:param num: номер окружения, кот. можно убить
        """

        server = libtmux.Server()
        session = server.find_where({"session_name": session_name}) if server.has_session(session_name) else None
        if session:
            session.kill_window(f'{self.WINDOW_NAME}{num}')
        else:
            raise ValueError(f'Bad session name {session_name}')

    def stop_all(self, session_name=SESSION_DEFAULT_NAME):
        """
        @:param session_name: Названия tmux-сессии, в которой запущены окружения
        """

        server = libtmux.Server()
        session = server.find_where({"session_name": session_name}) if server.has_session(session_name) else None
        logging.info(session)
        if session:
            for dir in self.created_dir:
                shutil.rmtree(dir)

            session.kill_session()
        else:
            raise ValueError(f'Bad session name {session_name}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tmux Jupyter notebook starter. Write your command',
                                     prog='Tmux jupyter starter')
    subparsers = parser.add_subparsers(title='command', help="Choose on of the commdands: \n start, "
                                                             "\n stop, \n stop_all", dest='command')

    parser_start = subparsers.add_parser('start')
    parser_start.add_argument('num_users', type=int, help='')
    parser_start.add_argument('base_dir', nargs='?', type=str, default='./', help='')
    parser_start.add_argument('--ip', '-a', type=str, default='0.0.0.0', help='')
    parser_start.add_argument('--ports', '-p', nargs='*', type=int, help='')

    parser_stop = subparsers.add_parser('stop')
    parser_stop.add_argument('session_name', type=str)
    parser_stop.add_argument('num', type=int)

    parser_stop_all = subparsers.add_parser('stop_all')
    parser_stop_all.add_argument('--session_name', type=str)

    args = parser.parse_args()
    logging.info(args)

    session_maker = TmuxJupyterSession()

    if args.command == 'start':
        session_maker.start(args.num_users, args.base_dir, args.ip, args.ports)
    elif args.command == 'stop':
        session_maker.stop(args.num, args.session_name)
    elif args.command == 'stop_all':
        if args.session_name:
            session_maker.stop_all(args.session_name)
        else:
            session_maker.stop_all()
