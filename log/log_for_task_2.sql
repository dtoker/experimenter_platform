BEGIN TRANSACTION;
CREATE TABLE "aoi" (
        `name`  TEXT NOT NULL,
        `task`  INTEGER NOT NULL,
        `dynamic`       INTEGER,
        `polygon`       BLOB,
        PRIMARY KEY(`name`,`task`)
);
INSERT INTO "aoi" VALUES('text',1,1,'[(0,0),(0,100),(100,100),(100,0)]');
INSERT INTO "aoi" VALUES('vis',1,1,'[(100,100),(100,200),(200,200),(200,100)]
');
INSERT INTO "aoi" VALUES('text',2,1,'[(0,100),(0,200),(100,200),(100,100)]
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
CREATE TABLE reading_proficiency ( `id` INTEGER, `time_stamp` INTEGER, `raw_prediction` REAL, `value` TEXT, PRIMARY KEY(`id`) );
CREATE TABLE `task_state` (
        `property`      TEXT NOT NULL,
        `value` INTEGER,
        PRIMARY KEY(`property`)
);
CREATE TABLE text_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
CREATE TABLE "user_state" (
        `event_name`    TEXT NOT NULL,
        `TYPE`  TEXT,
        `aoi`   TEXT,
        PRIMARY KEY(`event_name`)
);
INSERT INTO "user_state" VALUES('text_fix','fix','text');
INSERT INTO "user_state" VALUES('pupil','emdat','text');
INSERT INTO "user_state" VALUES('reading_proficiency','ml','');
INSERT INTO "user_state" VALUES('bad_type','same','text');
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
COMMIT;
