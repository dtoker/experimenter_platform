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
CREATE TABLE intervention_state ( `intervention` TEXT, `active` INTEGER, time_stamp INTEGER, occurences INTEGER, PRIMARY KEY(`intervention`));
INSERT INTO "intervention_state" VALUES('intervention_1',1,1530307440275297,3);
INSERT INTO "intervention_state" VALUES('intervention_2',1,1530307437818810,1);
CREATE TABLE pupil ( `id` INTEGER, `value` INTEGER, PRIMARY KEY(`id`) );
CREATE TABLE reading_proficiency ( `id` INTEGER, `time_stamp` INTEGER, `raw_prediction` REAL, `value` TEXT, PRIMARY KEY(`id`) );
CREATE TABLE rule_state ( `rule` TEXT, time_stamp INTEGER, occurences INTEGER, PRIMARY KEY(`rule`));
INSERT INTO "rule_state" VALUES('rule_1',1530307437818810,1);
INSERT INTO "rule_state" VALUES('rule_2',1530307440275297,2);
INSERT INTO "rule_state" VALUES('rule_3',1530307437818810,1);
CREATE TABLE `task_state` (
        `property`      TEXT NOT NULL,
        `value` INTEGER,
        PRIMARY KEY(`property`)
);
CREATE TABLE text_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
INSERT INTO "text_fix" VALUES(1,1530307437219285,1530307437385757,166472);
INSERT INTO "text_fix" VALUES(2,1530307437427509,1530307437818810,391301);
INSERT INTO "text_fix" VALUES(3,1530307440075331,1530307440275297,199966);
INSERT INTO "text_fix" VALUES(4,1530307442024131,1530307442132109,107978);
INSERT INTO "text_fix" VALUES(5,1530307442506935,1530307442648655,141720);
INSERT INTO "text_fix" VALUES(6,1530307446320882,1530307446595436,274554);
INSERT INTO "text_fix" VALUES(7,1530307446995251,1530307447136855,141604);
INSERT INTO "text_fix" VALUES(8,1530307448161055,1530307448294160,133105);
INSERT INTO "text_fix" VALUES(9,1530307450209606,1530307450376081,166475);
INSERT INTO "text_fix" VALUES(10,1530307450409326,1530307450542559,133233);
INSERT INTO "text_fix" VALUES(11,1530307452507507,1530307452632499,124992);
INSERT INTO "text_fix" VALUES(12,1530307452890570,1530307453007181,116611);
INSERT INTO "text_fix" VALUES(13,1530307456104685,1530307456213042,108357);
INSERT INTO "text_fix" VALUES(14,1530307456621111,1530307456762720,141609);
INSERT INTO "text_fix" VALUES(15,1530307456779347,1530307456937433,158086);
INSERT INTO "text_fix" VALUES(16,1530307457745444,1530307458103246,357802);
INSERT INTO "text_fix" VALUES(17,1530307461300616,1530307461492345,191729);
INSERT INTO "text_fix" VALUES(18,1530307466429946,1530307466738156,308210);
INSERT INTO "text_fix" VALUES(19,1530307467728871,1530307467837235,108364);
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
INSERT INTO "user_state" VALUES('vis_fix','fix','text');
CREATE TABLE "user_state_task" (
        `event_name`    TEXT,
        `task`  INTEGER,
        PRIMARY KEY(`event_name`,`task`)
);
INSERT INTO "user_state_task" VALUES('text_fix',1);
INSERT INTO "user_state_task" VALUES('text_fix',2);
INSERT INTO "user_state_task" VALUES('pupil',1);
INSERT INTO "user_state_task" VALUES('reading_proficiency',1);
INSERT INTO "user_state_task" VALUES('reading_proficiency',2);
INSERT INTO "user_state_task" VALUES('vis_fix',1);
CREATE TABLE vis_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
COMMIT;
