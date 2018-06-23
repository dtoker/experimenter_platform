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
INSERT INTO "intervention_state" VALUES('intervention_1',0,3000,3);
INSERT INTO "intervention_state" VALUES('intervention_2',1,6000,2);
CREATE TABLE pupil ( `id` INTEGER, `value` INTEGER, PRIMARY KEY(`id`) );
CREATE TABLE reading_proficiency ( `id` INTEGER, `time_stamp` INTEGER, `raw_prediction` REAL, `value` TEXT, PRIMARY KEY(`id`) );
CREATE TABLE rule_state ( `rule` TEXT, time_stamp INTEGER, occurences INTEGER, PRIMARY KEY(`rule`));
INSERT INTO "rule_state" VALUES('rule_1',2000,1);
INSERT INTO "rule_state" VALUES('rule_2',3000,2);
INSERT INTO "rule_state" VALUES('rule_3',6000,2);
CREATE TABLE `task_state` (
        `property`      TEXT NOT NULL,
        `value` INTEGER,
        PRIMARY KEY(`property`)
);
CREATE TABLE text_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
INSERT INTO "text_fix" VALUES(1,700,1200,200);
INSERT INTO "text_fix" VALUES(2,700,1200,200);
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
INSERT INTO "user_state_task" VALUES('pupil',2);
INSERT INTO "user_state_task" VALUES('reading_proficiency',3);
INSERT INTO "user_state_task" VALUES('reading_proficiency',2);
INSERT INTO "user_state_task" VALUES('vis_fix',1);
CREATE TABLE vis_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
COMMIT;
