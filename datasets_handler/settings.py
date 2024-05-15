"""Acesta este un modul ce detine clase si functii utile pentru aplicatie."""
from .models import UserIdentification
from datasets_handler import db
import re
import os
from shutil import rmtree


def verify_format_email(email: str):
    """ Verify if the email has a valid format.
        - cu r se incepe orice expresie regulata!
        - ^ inceputul sirului
        - \\S+ cauta cel putin un caracter care nu e spatiu alb
        - @ cauta acest caracter
        - \\. cauta un punct
        - $ semnifica sfarsitul sirului
        - [] doar din acest interval de caractere poate sa fie string-ul
        :param email: Get a string input
        :return: True
    """
    pattern = r'^\S+@\S+\.\S+$'
    match = re.match(pattern, email)
    return bool(match)


class CreateAdmin:
    """Se va crea un cont de administrator la initializarea aplicatiei!"""
    def __init__(self, admin_id, admin_pw):
        self.admin_id = admin_id
        self.admin_pw = admin_pw

    def set_admin(self):
        """
        Se creeaza contul de administrator la aplicatie!
        :return: None
        """
        data_db = db.session.execute(db.select(UserIdentification)).all()
        if not data_db:
            admin = UserIdentification(firstName="admin",  # type: ignore[call-arg]
                                       lastName="admin",  # type: ignore[call-arg]
                                       userName=self.admin_id,  # type: ignore[call-arg]
                                       email="empty@yahoo.com",  # type: ignore[call-arg]
                                       keyRole="Admin")  # type: ignore[call-arg]
            admin.set_password(key=self.admin_pw)
            db.session.add(admin)
            db.session.commit()
        else:
            print("Admin has been already created!")


class CreateDirectory:
    def __init__(self, path, dir_name="default"):
        self.path = path
        self.dir_name = dir_name
        self.path_maker = os.path.join(self.path, self.dir_name)

    def remove_dir(self):
        """
        Stergem un director care nu e gol!
        :return:
        """
        # os.path.basename() - returneaza ultimul obiect din calea catre un fisier/director
        if self.dir_name == "default":
            if os.path.exists(self.path):
                # sterge foldere care au in componenta sa alte documente, foldere etc.
                # os.rmdir sterge doar foldere goale
                rmtree(self.path)
            else:
                print(f"Directory {os.path.basename(self.path)} does\'t exist!")
        else:
            if os.path.exists(self.path_maker):
                # sterge foldere care au in componenta sa alte documente, foldere etc.
                # os.rmdir sterge doar foldere goale
                rmtree(self.path_maker)
            else:
                print(f"Directory {self.dir_name} does\'t exist!")

    def make_folder(self):
        """
        Creeaza un folder unde vor fi salvate fisierele
        :return: Calea absoluta catre director
        """
        if self.dir_name == "default":
            # Verificam sa nu existe acel folder
            if not os.path.exists(self.path):
                os.mkdir(self.path)
                print(f"Directory {os.path.basename(self.path)} has been successfully created!")
            else:
                print(f"Directory {os.path.basename(self.path)} exists!")
        else:
            if os.path.exists(self.path_maker):
                print(f'Directory {self.dir_name} has been already created!')
            else:
                os.mkdir(self.path_maker)
                print(f"Directory {self.dir_name} has been successfully created!")
