SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS GestionCommerciale
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE GestionCommerciale;


DROP TABLE IF EXISTS LIGNE_COMMANDE;
DROP TABLE IF EXISTS COMMANDE;
DROP TABLE IF EXISTS CLIENT;
DROP TABLE IF EXISTS PRODUIT;

CREATE TABLE PRODUIT (
    IDPROD        INT AUTO_INCREMENT PRIMARY KEY,
    NOM           VARCHAR(100)  NOT NULL,
    PRIX          DECIMAL(10,2) NOT NULL,
    QTTE          INT           NOT NULL DEFAULT 0,
    SEUIL_ALERTE  INT           NOT NULL DEFAULT 10,
    CONSTRAINT uq_produit_nom UNIQUE (NOM),
    CONSTRAINT ck_produit_prix  CHECK (PRIX >= 0),
    CONSTRAINT ck_produit_qtte  CHECK (QTTE >= 0),
    CONSTRAINT ck_produit_seuil CHECK (SEUIL_ALERTE >= 0)
) ENGINE=InnoDB;

CREATE TABLE CLIENT (
    IDCL   INT AUTO_INCREMENT PRIMARY KEY,
    NOMCL  VARCHAR(100) NOT NULL,
    EMAIL  VARCHAR(150) NOT NULL,
    VILLE  VARCHAR(80),
    CONSTRAINT uq_client_email UNIQUE (EMAIL),
    CONSTRAINT ck_client_email CHECK (EMAIL LIKE '%_@_%._%')
) ENGINE=InnoDB;

CREATE TABLE COMMANDE (
    IDCMD    INT AUTO_INCREMENT PRIMARY KEY,
    IDCL     INT         NOT NULL,
    DATECMD  DATE        NOT NULL,
    STATUT   VARCHAR(12) NOT NULL DEFAULT 'EN_ATTENTE',
    CONSTRAINT fk_commande_client FOREIGN KEY (IDCL)
        REFERENCES CLIENT(IDCL) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_commande_statut
        CHECK (STATUT IN ('EN_ATTENTE', 'VALIDEE', 'ANNULEE'))
) ENGINE=InnoDB;

CREATE TABLE LIGNE_COMMANDE (
    IDCMD     INT           NOT NULL,
    IDPROD    INT           NOT NULL,
    QTTECMD   INT           NOT NULL,
    PRIXVENTE DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (IDCMD, IDPROD),
    CONSTRAINT fk_ligne_commande FOREIGN KEY (IDCMD)
        REFERENCES COMMANDE(IDCMD) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_ligne_produit FOREIGN KEY (IDPROD)
        REFERENCES PRODUIT(IDPROD) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_ligne_qtte CHECK (QTTECMD > 0),
    CONSTRAINT ck_ligne_prix CHECK (PRIXVENTE >= 0)
) ENGINE=InnoDB;


INSERT INTO PRODUIT (IDPROD, NOM, PRIX, QTTE, SEUIL_ALERTE) VALUES
(1,  'Ordinateur Portable', 7500.00,  12,  5),
(2,  'Smartphone',          3600.00,  25, 10),
(3,  'Casque Audio',         580.00,  40, 15),
(4,  'Souris Optique',       120.00,   5, 10),   
(5,  'Clavier USB',          150.00,   3, 10),   
(6,  'Écran 24"',           1800.00,   8, 15),  
(7,  'Webcam HD',            350.00,   0, 10),  
(8,  'Imprimante Laser',    2200.00,  14,  5),
(9,  'Disque Dur Externe',   900.00,  30, 10),
(10, 'Clé USB 64 Go',         90.00, 100, 30),
(11, 'Enceinte Bluetooth',   450.00,   0, 10),   
(12, 'Routeur WiFi 6',       650.00,  18,  8),
(13, 'Tablette 10"',        2800.00,   9,  8),
(14, 'Chargeur Rapide',      180.00,  60, 20),
(15, 'Sac à dos PC',         320.00,  22, 10);   

INSERT INTO CLIENT (IDCL, NOMCL, EMAIL, VILLE) VALUES
(1,  'Ahmed Benali',      'ahmed.benali@mail.ma',   'Casablanca'),
(2,  'Fatima Zahra Idrissi','fz.idrissi@mail.ma',   'Rabat'),
(3,  'Youssef El Amrani', 'y.elamrani@mail.ma',     'Agadir'),
(4,  'Khadija Alaoui',    'k.alaoui@mail.ma',       'Marrakech'),
(5,  'Omar Tazi',         'omar.tazi@mail.ma',      'Fès'),
(6,  'Salma Berrada',     's.berrada@mail.ma',      'Tanger'),
(7,  'Hassan Ouazzani',   'h.ouazzani@mail.ma',     'Agadir'),
(8,  'Imane Chraibi',     'i.chraibi@mail.ma',      'Oujda'),
(9,  'Mehdi Lahlou',      'm.lahlou@mail.ma',       'Meknès'),
(10, 'Nadia Bennani',     'n.bennani@mail.ma',      'Tétouan');

INSERT INTO COMMANDE (IDCMD, IDCL, DATECMD, STATUT) VALUES
(1,  1,  '2025-01-10', 'VALIDEE'),
(2,  2,  '2025-01-22', 'VALIDEE'),
(3,  3,  '2025-02-05', 'VALIDEE'),
(4,  1,  '2025-02-18', 'VALIDEE'),
(5,  4,  '2025-03-03', 'VALIDEE'),
(6,  5,  '2025-03-15', 'VALIDEE'),
(7,  6,  '2025-03-28', 'ANNULEE'),
(8,  2,  '2025-04-04', 'VALIDEE'),
(9,  7,  '2025-04-12', 'VALIDEE'),
(10, 8,  '2025-04-20', 'VALIDEE'),
(11, 3,  '2025-05-06', 'VALIDEE'),
(12, 9,  '2025-05-19', 'ANNULEE'),
(13, 10, '2025-06-02', 'VALIDEE'),
(14, 1,  '2025-06-14', 'VALIDEE'),
(15, 4,  '2025-06-25', 'VALIDEE'),
(16, 5,  '2025-07-08', 'VALIDEE'),
(17, 6,  '2025-07-15', 'ANNULEE'),
(18, 7,  CURDATE() - INTERVAL 3  DAY, 'EN_ATTENTE'),
(19, 2,  CURDATE() - INTERVAL 45 DAY, 'EN_ATTENTE'),   
(20, 8,  CURDATE() - INTERVAL 1  DAY, 'EN_ATTENTE');   

INSERT INTO LIGNE_COMMANDE (IDCMD, IDPROD, QTTECMD, PRIXVENTE) VALUES
(1, 1, 1, 7500.00), (1, 3, 2, 580.00),  (1, 10, 5, 90.00),
(2, 2, 1, 3600.00), (2, 5, 2, 150.00),
(3, 6, 2, 1800.00), (3, 4, 3, 120.00),
(4, 8, 1, 2200.00), (4, 9, 2, 900.00),
(5, 2, 2, 3600.00), (5, 12, 1, 650.00),
(6, 3, 4, 580.00),  (6, 10, 10, 90.00),
(7, 1, 1, 7500.00),
(8, 13, 1, 2800.00),(8, 3, 1, 580.00),
(9, 9, 3, 900.00),  (9, 5, 1, 60.00),      -- prix très bas : anomalie
(10, 6, 1, 1800.00),(10, 12, 2, 650.00),
(11, 1, 2, 7500.00),(11, 2, 1, 3600.00),   -- montant élevé : anomalie
(12, 8, 2, 2200.00),
(13, 4, 5, 120.00), (13, 10, 20, 90.00), (13, 3, 2, 580.00),
(14, 2, 1, 3600.00),(14, 9, 1, 900.00),
(15, 6, 1, 1800.00),(15, 7, 2, 350.00),
(16, 11, 3, 450.00),(16, 1, 1, 7500.00),
(17, 12, 1, 650.00),
(18, 2, 1, 3600.00),(18, 3, 1, 580.00),
(19, 9, 2, 900.00), (19, 8, 1, 2200.00);


DROP PROCEDURE IF EXISTS AjouterProduit;
DROP PROCEDURE IF EXISTS ModifierStock;
DROP PROCEDURE IF EXISTS SupprimerProduit;
DROP FUNCTION  IF EXISTS ValeurStock;
DROP PROCEDURE IF EXISTS ProduitsEnAlerte;
DROP FUNCTION  IF EXISTS CalculerMontantCommande;
DROP PROCEDURE IF EXISTS CreerCommande;
DROP PROCEDURE IF EXISTS AjouterLigneCommande;
DROP PROCEDURE IF EXISTS ValiderCommande;
DROP PROCEDURE IF EXISTS AnnulerCommande;
DROP FUNCTION  IF EXISTS NombreCommandesClient;
DROP PROCEDURE IF EXISTS RapportStock;
DROP PROCEDURE IF EXISTS RapportClients;
DROP PROCEDURE IF EXISTS ClassementProduits;
DROP PROCEDURE IF EXISTS DetecterAnomalies;
DROP PROCEDURE IF EXISTS RapportAnnuel;

DELIMITER $$


CREATE PROCEDURE AjouterProduit(
    IN  p_nom   VARCHAR(100),
    IN  p_prix  DECIMAL(10,2),
    IN  p_qtte  INT,
    IN  p_seuil INT,
    OUT p_id    INT
)
BEGIN
    IF p_nom IS NULL OR TRIM(p_nom) = '' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nom de produit invalide';
    END IF;
    IF p_prix IS NULL OR p_prix < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Prix invalide';
    END IF;
    IF p_qtte IS NULL OR p_qtte < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantité invalide';
    END IF;
    IF p_seuil IS NULL OR p_seuil < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seuil d''alerte invalide';
    END IF;

    INSERT INTO PRODUIT (NOM, PRIX, QTTE, SEUIL_ALERTE)
    VALUES (TRIM(p_nom), p_prix, p_qtte, p_seuil);

    SET p_id = LAST_INSERT_ID();
END$$

-- Augmente (delta > 0) ou diminue (delta < 0) le stock
CREATE PROCEDURE ModifierStock(IN p_idprod INT, IN p_delta INT)
BEGIN
    DECLARE v_stock INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_delta IS NULL OR p_delta = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantité invalide';
    END IF;

    START TRANSACTION;

    SELECT QTTE INTO v_stock FROM PRODUIT WHERE IDPROD = p_idprod FOR UPDATE;

    IF v_stock IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Produit inexistant';
    END IF;
    IF v_stock + p_delta < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuffisant';
    END IF;

    UPDATE PRODUIT SET QTTE = QTTE + p_delta WHERE IDPROD = p_idprod;
    COMMIT;

    SELECT IDPROD, NOM, QTTE AS NOUVEAU_STOCK FROM PRODUIT WHERE IDPROD = p_idprod;
END$$

-- Supprime un produit uniquement s'il existe et n'a jamais été commandé
CREATE PROCEDURE SupprimerProduit(IN p_idprod INT)
BEGIN
    DECLARE v_existe INT DEFAULT 0;
    DECLARE v_lignes INT DEFAULT 0;

    SELECT COUNT(*) INTO v_existe FROM PRODUIT WHERE IDPROD = p_idprod;
    IF v_existe = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Produit inexistant';
    END IF;

    SELECT COUNT(*) INTO v_lignes FROM LIGNE_COMMANDE WHERE IDPROD = p_idprod;
    IF v_lignes > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Suppression impossible : produit présent dans des commandes';
    END IF;

    DELETE FROM PRODUIT WHERE IDPROD = p_idprod;
    SELECT 'Produit supprimé' AS Message;
END$$


CREATE FUNCTION ValeurStock()
RETURNS DECIMAL(15,2)
READS SQL DATA
BEGIN
    DECLARE v_valeur DECIMAL(15,2);
    SELECT IFNULL(SUM(PRIX * QTTE), 0) INTO v_valeur FROM PRODUIT;
    RETURN v_valeur;
END$$


CREATE PROCEDURE ProduitsEnAlerte()
BEGIN
    SELECT IDPROD, NOM, QTTE AS STOCK, SEUIL_ALERTE,
           CASE WHEN QTTE = 0 THEN 'Rupture' ELSE 'Faible' END AS STATUT
    FROM PRODUIT
    WHERE QTTE <= SEUIL_ALERTE
    ORDER BY QTTE, NOM;
END$$


CREATE FUNCTION CalculerMontantCommande(p_idcmd INT)
RETURNS DECIMAL(15,2)
READS SQL DATA
BEGIN
    DECLARE v_existe  INT DEFAULT 0;
    DECLARE v_montant DECIMAL(15,2);

    SELECT COUNT(*) INTO v_existe FROM COMMANDE WHERE IDCMD = p_idcmd;
    IF v_existe = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Commande inexistante';
    END IF;

    SELECT IFNULL(SUM(QTTECMD * PRIXVENTE), 0) INTO v_montant
    FROM LIGNE_COMMANDE WHERE IDCMD = p_idcmd;

    RETURN v_montant;
END$$

CREATE PROCEDURE CreerCommande(IN p_idcl INT, OUT p_idcmd INT)
BEGIN
    DECLARE v_existe INT DEFAULT 0;

    SELECT COUNT(*) INTO v_existe FROM CLIENT WHERE IDCL = p_idcl;
    IF v_existe = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Client inexistant';
    END IF;

    INSERT INTO COMMANDE (IDCL, DATECMD, STATUT)
    VALUES (p_idcl, CURDATE(), 'EN_ATTENTE');

    SET p_idcmd = LAST_INSERT_ID();
END$$

CREATE PROCEDURE AjouterLigneCommande(
    IN p_idcmd  INT,
    IN p_idprod INT,
    IN p_qte    INT
)
BEGIN
    DECLARE v_statut VARCHAR(12);
    DECLARE v_prix   DECIMAL(10,2);

    IF p_qte IS NULL OR p_qte <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantité invalide';
    END IF;

    SELECT STATUT INTO v_statut FROM COMMANDE WHERE IDCMD = p_idcmd;
    IF v_statut IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Commande inexistante';
    END IF;
    IF v_statut <> 'EN_ATTENTE' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Commande non modifiable (déjà validée ou annulée)';
    END IF;

    SELECT PRIX INTO v_prix FROM PRODUIT WHERE IDPROD = p_idprod;
    IF v_prix IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Produit inexistant';
    END IF;

    INSERT INTO LIGNE_COMMANDE (IDCMD, IDPROD, QTTECMD, PRIXVENTE)
    VALUES (p_idcmd, p_idprod, p_qte, v_prix)
    ON DUPLICATE KEY UPDATE QTTECMD = QTTECMD + p_qte;
END$$


CREATE PROCEDURE ValiderCommande(IN p_idcmd INT)
BEGIN
    DECLARE v_statut    VARCHAR(12);
    DECLARE v_nb_lignes INT DEFAULT 0;
    DECLARE v_manque    INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT STATUT INTO v_statut FROM COMMANDE WHERE IDCMD = p_idcmd FOR UPDATE;

    IF v_statut IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Commande inexistante';
    ELSEIF v_statut = 'VALIDEE' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Commande déjà validée';
    ELSEIF v_statut = 'ANNULEE' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Commande annulée : validation impossible';
    END IF;

    SELECT COUNT(*) INTO v_nb_lignes FROM LIGNE_COMMANDE WHERE IDCMD = p_idcmd;
    IF v_nb_lignes = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Commande vide : aucune ligne à valider';
    END IF;

    -- Verrouille les produits concernés et compte ceux dont le stock est insuffisant
    SELECT COUNT(*) INTO v_manque
    FROM LIGNE_COMMANDE L
    JOIN PRODUIT P ON P.IDPROD = L.IDPROD
    WHERE L.IDCMD = p_idcmd AND P.QTTE < L.QTTECMD
    FOR UPDATE;

    IF v_manque > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuffisant pour au moins un produit';
    END IF;

    UPDATE PRODUIT P
    JOIN LIGNE_COMMANDE L ON L.IDPROD = P.IDPROD
    SET P.QTTE = P.QTTE - L.QTTECMD
    WHERE L.IDCMD = p_idcmd;

    UPDATE COMMANDE SET STATUT = 'VALIDEE' WHERE IDCMD = p_idcmd;

    COMMIT;

    SELECT p_idcmd AS IDCMD, 'VALIDEE' AS STATUT,
           CalculerMontantCommande(p_idcmd) AS MONTANT;
END$$

CREATE PROCEDURE AnnulerCommande(IN p_idcmd INT)
BEGIN
    DECLARE v_statut VARCHAR(12);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT STATUT INTO v_statut FROM COMMANDE WHERE IDCMD = p_idcmd FOR UPDATE;

    IF v_statut IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Commande inexistante';
    ELSEIF v_statut = 'ANNULEE' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Commande déjà annulée';
    ELSEIF v_statut = 'VALIDEE' THEN
        UPDATE PRODUIT P
        JOIN LIGNE_COMMANDE L ON L.IDPROD = P.IDPROD
        SET P.QTTE = P.QTTE + L.QTTECMD
        WHERE L.IDCMD = p_idcmd;
    END IF;

    UPDATE COMMANDE SET STATUT = 'ANNULEE' WHERE IDCMD = p_idcmd;

    COMMIT;

    SELECT p_idcmd AS IDCMD, v_statut AS ANCIEN_STATUT, 'ANNULEE' AS NOUVEAU_STATUT;
END$$

CREATE FUNCTION NombreCommandesClient(p_idcl INT)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_existe INT DEFAULT 0;
    DECLARE v_nb     INT DEFAULT 0;

    SELECT COUNT(*) INTO v_existe FROM CLIENT WHERE IDCL = p_idcl;
    IF v_existe = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Client inexistant';
    END IF;

    SELECT COUNT(*) INTO v_nb FROM COMMANDE WHERE IDCL = p_idcl;
    RETURN v_nb;
END$$


CREATE PROCEDURE RapportStock()
BEGIN
    DECLARE v_id     INT;
    DECLARE v_nom    VARCHAR(100);
    DECLARE v_qtte   INT;
    DECLARE v_prix   DECIMAL(10,2);
    DECLARE v_seuil  INT;
    DECLARE v_etat   VARCHAR(10);

    DECLARE v_total   INT DEFAULT 0;
    DECLARE v_rupture INT DEFAULT 0;
    DECLARE v_faible  INT DEFAULT 0;
    DECLARE v_normal  INT DEFAULT 0;
    DECLARE v_valeur  DECIMAL(15,2) DEFAULT 0;
    DECLARE v_fin     INT DEFAULT 0;

    DECLARE cur CURSOR FOR
        SELECT IDPROD, NOM, QTTE, PRIX, SEUIL_ALERTE FROM PRODUIT ORDER BY IDPROD;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fin = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_rapport_stock;
    CREATE TEMPORARY TABLE tmp_rapport_stock (
        IDPROD INT, NOM VARCHAR(100), QTTE INT, SEUIL_ALERTE INT,
        VALEUR DECIMAL(15,2), ETAT VARCHAR(10)
    );

    OPEN cur;
    lecture: LOOP
        FETCH cur INTO v_id, v_nom, v_qtte, v_prix, v_seuil;
        IF v_fin = 1 THEN LEAVE lecture; END IF;

        IF v_qtte = 0 THEN
            SET v_etat = 'RUPTURE', v_rupture = v_rupture + 1;
        ELSEIF v_qtte <= v_seuil THEN
            SET v_etat = 'FAIBLE',  v_faible  = v_faible  + 1;
        ELSE
            SET v_etat = 'NORMAL',  v_normal  = v_normal  + 1;
        END IF;

        SET v_total  = v_total + 1;
        SET v_valeur = v_valeur + v_prix * v_qtte;

        INSERT INTO tmp_rapport_stock
        VALUES (v_id, v_nom, v_qtte, v_seuil, v_prix * v_qtte, v_etat);
    END LOOP;
    CLOSE cur;

    
    SELECT * FROM tmp_rapport_stock ORDER BY FIELD(ETAT, 'RUPTURE', 'FAIBLE', 'NORMAL'), NOM;

    SELECT 'Nombre total de produits' AS Indicateur, CAST(v_total AS CHAR) AS Valeur
    UNION ALL SELECT 'Produits en rupture',      CAST(v_rupture AS CHAR)
    UNION ALL SELECT 'Produits en stock faible', CAST(v_faible  AS CHAR)
    UNION ALL SELECT 'Produits en stock normal', CAST(v_normal  AS CHAR)
    UNION ALL SELECT 'Valeur totale du stock',   CONCAT(FORMAT(v_valeur, 2), ' DH');

    DROP TEMPORARY TABLE tmp_rapport_stock;
END$$


CREATE PROCEDURE RapportClients(IN p_seuil_vip DECIMAL(12,2))
BEGIN
    DECLARE v_id   INT;
    DECLARE v_nom  VARCHAR(100);
    DECLARE v_nb   INT;
    DECLARE v_ca   DECIMAL(15,2);
    DECLARE v_cat  VARCHAR(10);
    DECLARE v_fin  INT DEFAULT 0;

    DECLARE cur CURSOR FOR SELECT IDCL, NOMCL FROM CLIENT ORDER BY IDCL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fin = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_rapport_clients;
    CREATE TEMPORARY TABLE tmp_rapport_clients (
        IDCL INT, NOMCL VARCHAR(100), NB_COMMANDES_VALIDEES INT,
        CHIFFRE_AFFAIRES DECIMAL(15,2), CATEGORIE VARCHAR(10)
    );

    OPEN cur;
    lecture: LOOP
        FETCH cur INTO v_id, v_nom;
        IF v_fin = 1 THEN LEAVE lecture; END IF;

        SELECT COUNT(*) INTO v_nb
        FROM COMMANDE WHERE IDCL = v_id AND STATUT = 'VALIDEE';

        SELECT IFNULL(SUM(L.QTTECMD * L.PRIXVENTE), 0) INTO v_ca
        FROM COMMANDE C JOIN LIGNE_COMMANDE L ON L.IDCMD = C.IDCMD
        WHERE C.IDCL = v_id AND C.STATUT = 'VALIDEE';

        IF v_ca >= p_seuil_vip THEN SET v_cat = 'VIP';
        ELSEIF v_ca > 0        THEN SET v_cat = 'REGULIER';
        ELSE                        SET v_cat = 'INACTIF';
        END IF;

        INSERT INTO tmp_rapport_clients VALUES (v_id, v_nom, v_nb, v_ca, v_cat);
    END LOOP;
    CLOSE cur;

    SELECT * FROM tmp_rapport_clients ORDER BY CHIFFRE_AFFAIRES DESC;
    DROP TEMPORARY TABLE tmp_rapport_clients;
END$$

CREATE PROCEDURE ClassementProduits()
BEGIN
    DECLARE v_id      INT;
    DECLARE v_nom     VARCHAR(100);
    DECLARE v_qte     INT;
    DECLARE v_ca      DECIMAL(15,2);
    DECLARE v_pos     INT DEFAULT 0;
    DECLARE v_rang    INT DEFAULT 0;
    DECLARE v_prec_ca DECIMAL(15,2) DEFAULT NULL;
    DECLARE v_fin     INT DEFAULT 0;

    DECLARE cur CURSOR FOR
        SELECT P.IDPROD, P.NOM,
               IFNULL(SUM(V.QTTECMD), 0)               AS QTE_VENDUE,
               IFNULL(SUM(V.QTTECMD * V.PRIXVENTE), 0) AS CA
        FROM PRODUIT P
        LEFT JOIN (
            SELECT L.IDPROD, L.QTTECMD, L.PRIXVENTE
            FROM LIGNE_COMMANDE L
            JOIN COMMANDE C ON C.IDCMD = L.IDCMD
            WHERE C.STATUT = 'VALIDEE'
        ) V ON V.IDPROD = P.IDPROD
        GROUP BY P.IDPROD, P.NOM
        ORDER BY CA DESC, P.NOM;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fin = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_classement;
    CREATE TEMPORARY TABLE tmp_classement (
        RANG INT, IDPROD INT, NOM VARCHAR(100),
        QTE_VENDUE INT, CHIFFRE_AFFAIRES DECIMAL(15,2)
    );

    OPEN cur;
    lecture: LOOP
        FETCH cur INTO v_id, v_nom, v_qte, v_ca;
        IF v_fin = 1 THEN LEAVE lecture; END IF;

        SET v_pos = v_pos + 1;
        -- Les ex æquo (même CA) partagent le même rang
        IF v_prec_ca IS NULL OR v_ca <> v_prec_ca THEN
            SET v_rang = v_pos;
        END IF;
        SET v_prec_ca = v_ca;

        INSERT INTO tmp_classement VALUES (v_rang, v_id, v_nom, v_qte, v_ca);
    END LOOP;
    CLOSE cur;

    SELECT * FROM tmp_classement ORDER BY RANG, NOM;
    DROP TEMPORARY TABLE tmp_classement;
END$$

CREATE PROCEDURE DetecterAnomalies()
BEGIN
    DECLARE v_id      INT;
    DECLARE v_statut  VARCHAR(12);
    DECLARE v_date    DATE;
    DECLARE v_nb      INT;
    DECLARE v_montant DECIMAL(15,2);
    DECLARE v_ecart   INT;
    DECLARE v_fin     INT DEFAULT 0;

    DECLARE cur CURSOR FOR SELECT IDCMD, STATUT, DATECMD FROM COMMANDE ORDER BY IDCMD;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fin = 1;

    DROP TEMPORARY TABLE IF EXISTS tmp_anomalies;
    CREATE TEMPORARY TABLE tmp_anomalies (
        IDCMD INT, STATUT VARCHAR(12), ANOMALIE VARCHAR(120)
    );

    OPEN cur;
    lecture: LOOP
        FETCH cur INTO v_id, v_statut, v_date;
        IF v_fin = 1 THEN LEAVE lecture; END IF;

        SELECT COUNT(*) INTO v_nb FROM LIGNE_COMMANDE WHERE IDCMD = v_id;
        SET v_montant = CalculerMontantCommande(v_id);

        SELECT COUNT(*) INTO v_ecart
        FROM LIGNE_COMMANDE L JOIN PRODUIT P ON P.IDPROD = L.IDPROD
        WHERE L.IDCMD = v_id AND ABS(L.PRIXVENTE - P.PRIX) > 0.5 * P.PRIX;

        IF v_nb = 0 THEN
            INSERT INTO tmp_anomalies VALUES (v_id, v_statut, 'Commande sans ligne');
        END IF;
        IF v_statut = 'EN_ATTENTE' AND DATEDIFF(CURDATE(), v_date) > 30 THEN
            INSERT INTO tmp_anomalies
            VALUES (v_id, v_statut, 'En attente depuis plus de 30 jours');
        END IF;
        IF v_montant > 15000 THEN
            INSERT INTO tmp_anomalies
            VALUES (v_id, v_statut, 'Montant exceptionnellement élevé (> 15 000 DH)');
        END IF;
        IF v_ecart > 0 THEN
            INSERT INTO tmp_anomalies
            VALUES (v_id, v_statut, 'Prix de vente éloigné de plus de 50 % du prix catalogue');
        END IF;
    END LOOP;
    CLOSE cur;

    SELECT A.IDCMD, C.IDCL, C.DATECMD, A.STATUT, A.ANOMALIE
    FROM tmp_anomalies A JOIN COMMANDE C ON C.IDCMD = A.IDCMD
    ORDER BY A.IDCMD;

    DROP TEMPORARY TABLE tmp_anomalies;
END$$


CREATE PROCEDURE RapportAnnuel(IN p_annee INT)
BEGIN
    DECLARE v_id       INT;
    DECLARE v_nom      VARCHAR(100);
    DECLARE v_valid    INT;
    DECLARE v_annul    INT;
    DECLARE v_ca       DECIMAL(15,2);
    DECLARE v_panier   DECIMAL(15,2);

    DECLARE t_ca       DECIMAL(15,2) DEFAULT 0;
    DECLARE t_valid    INT DEFAULT 0;
    DECLARE t_annul    INT DEFAULT 0;
    DECLARE t_actifs   INT DEFAULT 0;
    DECLARE v_best_ca  DECIMAL(15,2) DEFAULT 0;
    DECLARE v_best_nom VARCHAR(100) DEFAULT 'Aucun';
    DECLARE v_fin      INT DEFAULT 0;

    DECLARE cur CURSOR FOR SELECT IDCL, NOMCL FROM CLIENT ORDER BY IDCL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fin = 1;

    IF p_annee IS NULL OR p_annee < 2000 OR p_annee > 2100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Année invalide';
    END IF;

    DROP TEMPORARY TABLE IF EXISTS tmp_annuel;
    CREATE TEMPORARY TABLE tmp_annuel (
        IDCL INT, NOMCL VARCHAR(100), COMMANDES_VALIDEES INT,
        COMMANDES_ANNULEES INT, CHIFFRE_AFFAIRES DECIMAL(15,2), PANIER_MOYEN DECIMAL(15,2)
    );

    OPEN cur;
    lecture: LOOP
        FETCH cur INTO v_id, v_nom;
        IF v_fin = 1 THEN LEAVE lecture; END IF;

        SELECT COUNT(*) INTO v_valid FROM COMMANDE
        WHERE IDCL = v_id AND STATUT = 'VALIDEE' AND YEAR(DATECMD) = p_annee;

        SELECT COUNT(*) INTO v_annul FROM COMMANDE
        WHERE IDCL = v_id AND STATUT = 'ANNULEE' AND YEAR(DATECMD) = p_annee;

        SELECT IFNULL(SUM(L.QTTECMD * L.PRIXVENTE), 0) INTO v_ca
        FROM COMMANDE C JOIN LIGNE_COMMANDE L ON L.IDCMD = C.IDCMD
        WHERE C.IDCL = v_id AND C.STATUT = 'VALIDEE' AND YEAR(C.DATECMD) = p_annee;

        SET v_panier = IF(v_valid > 0, v_ca / v_valid, 0);

        SET t_ca    = t_ca + v_ca;
        SET t_valid = t_valid + v_valid;
        SET t_annul = t_annul + v_annul;
        IF v_valid > 0 THEN SET t_actifs = t_actifs + 1; END IF;
        IF v_ca > v_best_ca THEN
            SET v_best_ca = v_ca, v_best_nom = v_nom;
        END IF;

        INSERT INTO tmp_annuel VALUES (v_id, v_nom, v_valid, v_annul, v_ca, v_panier);
    END LOOP;
    CLOSE cur;

    SELECT * FROM tmp_annuel ORDER BY CHIFFRE_AFFAIRES DESC;

    SELECT CONCAT('Chiffre d''affaires ', p_annee) AS Indicateur,
           CONCAT(FORMAT(t_ca, 2), ' DH') AS Valeur
    UNION ALL SELECT 'Commandes validées',  CAST(t_valid  AS CHAR)
    UNION ALL SELECT 'Commandes annulées',  CAST(t_annul  AS CHAR)
    UNION ALL SELECT 'Clients actifs',      CAST(t_actifs AS CHAR)
    UNION ALL SELECT 'Meilleur client',     CONCAT(v_best_nom, ' (', FORMAT(v_best_ca, 2), ' DH)');

    DROP TEMPORARY TABLE tmp_annuel;
END$$

DELIMITER ;

SET @id = 0;
CALL AjouterProduit('Hub USB-C', 250.00, 30, 10, @id);
SELECT @id AS NOUVEAU_ID;
CALL ModifierStock(@id, 20);
CALL ModifierStock(@id, -10);
SELECT ValeurStock() AS VALEUR_TOTALE_STOCK;
CALL ProduitsEnAlerte();
CALL SupprimerProduit(@id);          

SET @cmd = 0;
CALL CreerCommande(3, @cmd);
CALL AjouterLigneCommande(@cmd, 2, 1);
CALL AjouterLigneCommande(@cmd, 10, 4);
SELECT CalculerMontantCommande(@cmd) AS MONTANT;
CALL ValiderCommande(@cmd);
SELECT IDPROD, NOM, QTTE FROM PRODUIT WHERE IDPROD IN (2, 10);   
CALL AnnulerCommande(@cmd);                                       
SELECT NombreCommandesClient(1) AS NB_COMMANDES_CLIENT_1;


CALL RapportStock();
CALL RapportClients(10000);
CALL ClassementProduits();
CALL DetecterAnomalies();
CALL RapportAnnuel(2025);

