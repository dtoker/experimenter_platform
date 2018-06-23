BEGIN TRANSACTION;
CREATE TABLE "aoi" (
        `name`  TEXT NOT NULL,
        `task`  INTEGER NOT NULL,
        `dynamic`       INTEGER,
        `polygon`       BLOB,
        PRIMARY KEY(`name`,`task`)
);
INSERT INTO "aoi" VALUES('text',1,1,'[(0,0),(300,0),(300,300),(0,300)]');
INSERT INTO "aoi" VALUES('vis',1,1,'[(1000,800),(1280,800),(1280,1080),(1000,1080)]
');
INSERT INTO "aoi" VALUES('text',2,1,'[(0,0),(200,0),(0,200),(200,200)]
');
CREATE TABLE "aoi_state" (
        `aoi`   TEXT,
        `task`  INTEGER,
        `active`        INTEGER,
        PRIMARY KEY(`aoi`)
);
CREATE TABLE `intervention_state` (
        `intervention`  TEXT NOT NULL,
        `active`        INTEGER,
        `time_stamp`    INTEGER,
        `occurences`    INTEGER,
        PRIMARY KEY(`intervention`)
);
CREATE TABLE `task_state` (
        `property`      TEXT NOT NULL,
        `value` INTEGER,
        PRIMARY KEY(`property`)
);
CREATE TABLE text_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
INSERT INTO "text_fix" VALUES(1,1529712732490736,1529712732682198,191462);
INSERT INTO "text_fix" VALUES(2,1529712732773943,1529712733057020,283077);
INSERT INTO "text_fix" VALUES(3,1529712733123631,1529712733231732,108101);
INSERT INTO "text_fix" VALUES(4,1529712733381583,1529712733581430,199847);
INSERT INTO "text_fix" VALUES(5,1529712733856525,1529712733972991,116466);
INSERT INTO "text_fix" VALUES(6,1529712733989614,1529712734097844,108230);
INSERT INTO "text_fix" VALUES(7,1529712734414160,1529712734530765,116605);
INSERT INTO "text_fix" VALUES(8,1529712736312840,1529712736504314,191474);
INSERT INTO "text_fix" VALUES(9,1529712736554182,1529712736687532,133350);
INSERT INTO "text_fix" VALUES(10,1529712736695775,1529712736987363,291588);
INSERT INTO "text_fix" VALUES(11,1529712737811585,1529712737961429,149844);
INSERT INTO "text_fix" VALUES(12,1529712737969810,1529712738111402,141592);
INSERT INTO "text_fix" VALUES(13,1529712738128026,1529712738253016,124990);
CREATE TABLE "user_state" (
        `event_name`    TEXT NOT NULL,
        `TYPE`  TEXT,
        `aoi`   TEXT,
        PRIMARY KEY(`event_name`)
);
INSERT INTO "user_state" VALUES('text_fix','fix','text');
INSERT INTO "user_state" VALUES('pupil','emdat','vis');
INSERT INTO "user_state" VALUES('reading_proficiency','ml','');
INSERT INTO "user_state" VALUES('bad_type','same','text');
CREATE TABLE "user_state_task" (
        `event_name`    TEXT,
        `task`  INTEGER,
        PRIMARY KEY(`event_name`,`task`)
);
INSERT INTO "user_state_task" VALUES('text_fix',1);
INSERT INTO "user_state_task" VALUES('text_fix',2);
INSERT INTO "user_state_task" VALUES('pupil',2);
INSERT INTO "user_state_task" VALUES('reading_proficiency',3);
INSERT INTO "user_state_task" VALUES('reading_proficiency',2);
COMMIT;
