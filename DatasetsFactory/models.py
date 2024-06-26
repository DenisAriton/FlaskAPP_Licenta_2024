from DatasetsFactory import db
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import Integer, VARCHAR, TIMESTAMP, TEXT, Enum, ForeignKey, text, Float
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class UserIdentification(db.Model, UserMixin):
    __tablename__ = "user_identification"
    idUser = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    firstName = mapped_column(VARCHAR(255), nullable=False)
    lastName = mapped_column(VARCHAR(255), nullable=False)
    userName = mapped_column(VARCHAR(255), unique=True, nullable=False)
    email = mapped_column(VARCHAR(255), unique=True, nullable=False)
    ImageName = mapped_column(VARCHAR(255), unique=True, nullable=True)
    keyPass = mapped_column(VARCHAR(255), unique=True, nullable=False)
    keyRole = mapped_column(VARCHAR(255), nullable=False, server_default='User')
    TokenKey = mapped_column(VARCHAR(255), unique=True, nullable=True)
    # Momentul inregistrarii
    timeRegistered = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    # Momentul resetarii informatiilor personale
    timeReset = mapped_column(TIMESTAMP, nullable=True)
    # Aici se definesc relatiile dintre tabele - aceasta este forma non-annotated
    relSession = relationship("UserSession")
    relLog = relationship("LogFile", back_populates="user_log")
    groups = relationship("UserGroup", back_populates="userId")

    def get_id(self):
        """
        Trebuie suprascrisa metoda clasei UserMixin, deoarece va cauta atributul id, iar noi avem definit idUser!
        :return: idUser
        """
        return self.idUser

    def set_password(self, key):
        """Creeaza o parola securizata - hash!"""
        self.keyPass = generate_password_hash(key)

    def check_password(self, keypass):
        """Verificam hash-ul!"""
        return check_password_hash(self.keyPass, keypass)


class Groups(db.Model):
    """
    Acest tabel va detine toate grupele create de admin.
    idGroup: id-ul grupului
    groupName: denumirea grupului dat de admin
    """
    __tablename__ = "groups"
    idGroup = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    groupName = mapped_column(VARCHAR(255), unique=True, nullable=False)
    members = mapped_column(Integer, nullable=True)
    userGr = relationship("UserGroup", back_populates="groupsId")
    file = relationship("FileAccess", back_populates="groups")


class UserGroup(db.Model):
    """
    Acest tabel detine grupele la care au fost asignati userii.
    idUserGroup: id-ul grupului
    idUser: FK al user-ului
    idGroup: FK al grupului
    """
    __tablename__ = "user_group"
    idUserGroup = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    idUser = mapped_column(Integer, ForeignKey('user_identification.idUser'), unique=True, nullable=False)
    idGroup = mapped_column(Integer, ForeignKey('groups.idGroup'), nullable=False)
    # Pentru acest tip de asociere, am creat o relatie de many-to-many bidirectionala!
    # Ca sa pot accesa toti userii asignati unei anumite grupe.
    groupsId = relationship("Groups", back_populates="userGr")
    userId = relationship("UserIdentification", back_populates="groups")


class UserSession(db.Model):
    """
    Se pastreaza istoricul conectarilor la site!
    - se va introduce o singura data iduser-ul in acest tabel la prima conexiune
    - apoi sa va verifica sa nu fie in acest tabel user-ul, daca nu este atunci la a doua logare se va face update pe startTime
    TODO : Va trebui implementat un CRON job pentru golirea tabelului odata la luna!
    """
    __tablename__ = "user_session"
    idSession = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    idUser = mapped_column(Integer, ForeignKey('user_identification.idUser'), nullable=False)
    # Momentul logarii
    startTime = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    # Momentul delogarii!
    endTime = mapped_column(TIMESTAMP, nullable=True)


class Datasets(db.Model):
    """
    Acesta este un tabel care retine numele directoarelor(dataseturilor).
    """
    __tablename__ = "datasets"
    idDataset = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    directory = mapped_column(VARCHAR(100), nullable=False, unique=True)
    description = mapped_column(TEXT, nullable=True)
    TimeCreated = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    dataset_files = relationship("FilesInDataset", back_populates="relation_dataset")
    get_access = relationship("FileAccess", back_populates="datasets_access")


class DataFiles(db.Model):
    """
    Retinem datele specifice unui fisier!
    nume, extensie, size, unitate de masura, relativePath, numar de coloane si linii, momentul upload-ului
    """
    __tablename__ = "data_files"
    idFile = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    fileName = mapped_column(VARCHAR(255), unique=True, nullable=True)
    extension = mapped_column(VARCHAR(15), nullable=True)  # .txt, .pdf, .csv, .doc, .xlsx
    size = mapped_column(Float, nullable=True)
    sizeUnit = mapped_column(Enum("KB", "MB", "GB"), nullable=True)
    relativePath = mapped_column(VARCHAR(255), nullable=True)
    columnNr = mapped_column(Integer, nullable=True)
    rowNr = mapped_column(Integer, nullable=True)
    uploadTime = mapped_column(TIMESTAMP, nullable=False)
    file_in_dataset = relationship("FilesInDataset", back_populates="relation_file")
    log_file = relationship("LogFile", back_populates="file_log")


class FilesInDataset(db.Model):
    """
    Tabel relational intre fisiere si dataseturi, pentru a pastra ce fisiere sunt salvate intr-un anume dataset
    """
    __tablename__ = "files_in_dataset"
    idFilesInDataset = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    idDataset = mapped_column(Integer, ForeignKey('datasets.idDataset'), nullable=False)
    idFile = mapped_column(Integer, ForeignKey('data_files.idFile'), nullable=False)
    relation_file = relationship("DataFiles", back_populates="file_in_dataset")
    relation_dataset = relationship("Datasets", back_populates="dataset_files")


class FileAccess(db.Model):
    """
    Acesta este un tabel care da drepturi de acces pe un anume fisier de date!
    """
    __tablename__ = "file_access"
    idAccess = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    idGroup = mapped_column(Integer, ForeignKey('groups.idGroup'), nullable=False)
    idDataset = mapped_column(Integer, ForeignKey('datasets.idDataset'), nullable=False)
    keyAccess = mapped_column(Integer, nullable=True)
    # Momentul in care s-a dat access la dataset!
    TimeGetAccess = mapped_column(TIMESTAMP, nullable=True, server_default=text('CURRENT_TIMESTAMP'))
    # Momentul in care s-a luat dreptul de acces pe dataset!
    TimeTakeAccess = mapped_column(TIMESTAMP, nullable=True)

    groups = relationship("Groups", back_populates="file")
    datasets_access = relationship("Datasets", back_populates="get_access")


class LogFile(db.Model):
    """
    Se pastreaza un istoric al accesarilor de fisiere, cine a accesat si in ce moment!
    """
    __tablename__ = "log_file"
    idLog = mapped_column(Integer, primary_key=True, nullable=False)
    idUser = mapped_column(Integer, ForeignKey('user_identification.idUser'), nullable=False)
    idFile = mapped_column(Integer, ForeignKey('data_files.idFile'), nullable=False)
    # Momentul cand s-a accesat fisierul
    timeAccess = mapped_column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    user_log = relationship("UserIdentification", back_populates="relLog")
    file_log = relationship("DataFiles", back_populates="log_file")
