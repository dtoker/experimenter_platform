BEGIN TRANSACTION;
CREATE TABLE "aoi" (
        `name`  TEXT NOT NULL,
        `task`  INTEGER NOT NULL,
        `dynamic`       INTEGER,
        `polygon`       BLOB,
        PRIMARY KEY(`name`,`task`)
);
INSERT INTO "aoi" VALUES('text',1,1,'[(0,0),(300,0),(300,300),(0,300)]');
INSERT INTO "aoi" VALUES('text',2,1,'[(0,0),(200,0),(0,200),(200,200)]
');
INSERT INTO "aoi" VALUES('vis',2,1,'[(1000,800),(1280,800),(1280,1080),(1000,1080)]');
INSERT INTO "aoi" VALUES('t3_aoi1',3,1,'[(0,0),(200,0),(0,200),(200,200)]');
INSERT INTO "aoi" VALUES('t3_aoi2',3,1,'[(1000,800),(1280,800),(1280,1080),(1000,1080)]');
INSERT INTO "aoi" VALUES('t3_aoi3',3,1,'[(300,300),(300,600),(600,300),(600,600)]');
INSERT INTO "aoi" VALUES('t3_aoi4',3,1,'[(800,300),(800,500),(1000,300),(1000,500)]');
INSERT INTO "aoi" VALUES('t3_aoi5',3,1,'[(1000, 0),(1000,200),(1280,0),(1280,200)]');
INSERT INTO "aoi" VALUES('t4_aoi1',4,1,'[(0,0),(200,0),(0,200),(200,200)]');
INSERT INTO "aoi" VALUES('t4_aoi2',4,1,'[(1000,800),(1280,800),(1280,1080),(1000,1080)]');
INSERT INTO "aoi" VALUES('t4_aoi3',4,1,'[(300,300),(300,600),(600,300),(600,600)]');
INSERT INTO "aoi" VALUES('t4_aoi4',4,1,'[(800,300),(800,500),(1000,300),(1000,500)]');
INSERT INTO "aoi" VALUES('t4_aoi5',4,1,'[(1000, 0),(1000,200),(1280,0),(1280,200)]');
INSERT INTO "aoi" VALUES('t4_aoi6',4,1,'[(600,600),(800,600),(600,800),(800,800)]');
INSERT INTO "aoi" VALUES('t4_aoi7',4,1,'[(300,900),(300,1100),(500,900),(500,1100)]');
INSERT INTO "aoi" VALUES('vis',1,1,'[(1000,800),(1280,800),(1280,1080),(1000,1080)]');
CREATE TABLE "aoi_state" (
        `aoi`   TEXT,
        `task`  INTEGER,
        `active`        INTEGER,
        PRIMARY KEY(`aoi`)
);
CREATE TABLE intervention_state ( `intervention` TEXT, `active` INTEGER, time_stamp INTEGER, occurences INTEGER, PRIMARY KEY(`intervention`));
INSERT INTO "intervention_state" VALUES('intervention_2',0,1531957577258219,2);
INSERT INTO "intervention_state" VALUES('intervention_1',0,1531957577258219,2);
CREATE TABLE pupil ( `id` INTEGER, `interval_value` INTEGER, `task_value` TEXT, `runtime_value` TEXT, PRIMARY KEY(`id`) );
INSERT INTO "pupil" VALUES(2,-1,'-1','-1');
INSERT INTO "pupil" VALUES(3,-1,'-1','-1');
INSERT INTO "pupil" VALUES(4,-1,'-1','-1');
INSERT INTO "pupil" VALUES(5,-1,'-1','-1');
INSERT INTO "pupil" VALUES(6,-1,'-1','-1');
INSERT INTO "pupil" VALUES(7,-1,'-1','-1');
INSERT INTO "pupil" VALUES(8,-1,'-1','-1');
INSERT INTO "pupil" VALUES(9,-1,'-1','-1');
INSERT INTO "pupil" VALUES(10,-1,'-1','-1');
INSERT INTO "pupil" VALUES(11,-1,'-1','-1');
INSERT INTO "pupil" VALUES(12,-1,'-1','-1');
INSERT INTO "pupil" VALUES(13,-1,'-1','-1');
INSERT INTO "pupil" VALUES(14,-1,'-1','-1');
INSERT INTO "pupil" VALUES(15,-1,'-1','-1');
INSERT INTO "pupil" VALUES(16,-1,'-1','-1');
INSERT INTO "pupil" VALUES(17,-1,'-1','-1');
INSERT INTO "pupil" VALUES(18,-1,'-1','-1');
INSERT INTO "pupil" VALUES(19,-1,'-1','-1');
INSERT INTO "pupil" VALUES(20,-1,'-1','-1');
INSERT INTO "pupil" VALUES(21,-1,'-1','-1');
INSERT INTO "pupil" VALUES(22,-1,'-1','-1');
INSERT INTO "pupil" VALUES(23,-1,'-1','-1');
INSERT INTO "pupil" VALUES(24,-1,'-1','-1');
INSERT INTO "pupil" VALUES(25,3.27751996440272197474e+00,'3.27751996440272','3.27751996440272');
INSERT INTO "pupil" VALUES(26,3.29017744393184274898e+00,'3.28363774617513','3.28363774617513');
INSERT INTO "pupil" VALUES(27,-1,'3.28363774617513','3.28363774617513');
INSERT INTO "pupil" VALUES(28,-1,'3.28363774617513','3.28363774617513');
INSERT INTO "pupil" VALUES(29,-1,'3.28363774617513','3.28363774617513');
INSERT INTO "pupil" VALUES(30,2.76398754119873046875e+00,'3.22250242794261','3.22250242794261');
INSERT INTO "pupil" VALUES(31,3.33929347991943359375e+00,'3.26575837311921','3.26575837311921');
INSERT INTO "pupil" VALUES(32,3.32809106234846430183e+00,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(33,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(34,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(35,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(36,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(37,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(38,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(39,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(40,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(41,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(42,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(43,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(44,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(45,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(46,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(47,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(48,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(49,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(50,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(51,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(52,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(53,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(54,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(55,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(56,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(57,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(58,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(59,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(60,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(61,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(62,-1,'3.28753726453666','3.28753726453666');
INSERT INTO "pupil" VALUES(63,-1,'3.28753726453666','3.28753726453666');
CREATE TABLE reading_proficiency ( `id` INTEGER, `time_stamp` INTEGER, `raw_prediction` REAL, `value` TEXT, PRIMARY KEY(`id`) );
CREATE TABLE rule_state ( `rule` TEXT, time_stamp INTEGER, occurences INTEGER, PRIMARY KEY(`rule`));
INSERT INTO "rule_state" VALUES('rule_3',1531957577258219,2);
INSERT INTO "rule_state" VALUES('rule_1',1531957418394949,1);
INSERT INTO "rule_state" VALUES('rule_2',1531957577258219,1);
CREATE TABLE `task_state` (
        `property`      TEXT NOT NULL,
        `value` INTEGER,
        PRIMARY KEY(`property`)
);
CREATE TABLE text_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
INSERT INTO "text_fix" VALUES(1,1531957414939330,1531957415064207,124877);
INSERT INTO "text_fix" VALUES(2,1531957418095244,1531957418394949,299705);
INSERT INTO "text_fix" VALUES(3,1531957424481810,1531957425206224,724414);
INSERT INTO "text_fix" VALUES(4,1531957525291253,1531957525799191,507938);
INSERT INTO "text_fix" VALUES(7,1531957577124987,1531957577258219,133232);
CREATE TABLE "user_state" (
	`event_name`	TEXT NOT NULL,
	`type`	TEXT,
	`aoi`	TEXT,
	`feature`	TEXT,
	PRIMARY KEY(`event_name`)
);
INSERT INTO "user_state" VALUES('text_fix','fix','text','');
INSERT INTO "user_state" VALUES('pupil','emdat','vis','meanpupilsize');
INSERT INTO "user_state" VALUES('reading_proficiency','ml','',NULL);
INSERT INTO "user_state" VALUES('vis_fix','fix','vis',NULL);
INSERT INTO "user_state" VALUES('text_1_emdat','emdat','text_1','meanpupilsize');
INSERT INTO "user_state" VALUES('text_2_emdat','emdat','text_2','meanpupilvelocity');
INSERT INTO "user_state" VALUES('task_1_fixrate','emdat','text','fixationrate');
INSERT INTO "user_state" VALUES('task_1_3_emdat','emdat','t3_aoi1','fixationrate');
INSERT INTO "user_state" VALUES('task_2_3_emdat','emdat','t3_aoi2','meanpupilvelocity');
INSERT INTO "user_state" VALUES('task_3_3_emdat','emdat','t3_aoi3','meanpupilsize');
INSERT INTO "user_state" VALUES('task_4_3_emdat','emdat','t3_aoi4','meandistance');
INSERT INTO "user_state" VALUES('task_5_3_emdat','emdat','t3_aoi5','stddevdistance');
INSERT INTO "user_state" VALUES('task_1_4_emdat','emdat','t4_aoi1','meanpupilvelocity');
INSERT INTO "user_state" VALUES('task_2_4_emdat','emdat','t4_aoi2','meanpupilsize');
INSERT INTO "user_state" VALUES('task_3_4_emdat','emdat','t4_aoi3','meandistance');
INSERT INTO "user_state" VALUES('task_4_4_emdat','emdat','t4_aoi4','stddevdistance');
INSERT INTO "user_state" VALUES('task_5_4_emdat','emdat','t4_aoi5','fixationrate');
INSERT INTO "user_state" VALUES('task_6_4_emdat','emdat','t4_aoi6','meanfixationduration');
INSERT INTO "user_state" VALUES('task_7_4_emdat','emdat','t4_aoi7','stddevfixationduration');
INSERT INTO "user_state" VALUES('bad_type','same','text',NULL);
INSERT INTO "user_state" VALUES('task_2_2_emdat','emdat','text','maxpupilsize');
CREATE TABLE "user_state_task" (
        `event_name`    TEXT,
        `task`  INTEGER,
        PRIMARY KEY(`event_name`,`task`)
);
INSERT INTO "user_state_task" VALUES('text_fix',1);
INSERT INTO "user_state_task" VALUES('pupil',2);
INSERT INTO "user_state_task" VALUES('pupil',1);
INSERT INTO "user_state_task" VALUES('reading_proficiency',1);
INSERT INTO "user_state_task" VALUES('reading_proficiency',2);
INSERT INTO "user_state_task" VALUES('vis_fix',1);
INSERT INTO "user_state_task" VALUES('task_1_3_emdat',3);
INSERT INTO "user_state_task" VALUES('task_2_3_emdat',3);
INSERT INTO "user_state_task" VALUES('task_3_3_emdat',3);
INSERT INTO "user_state_task" VALUES('task_4_3_emdat',3);
INSERT INTO "user_state_task" VALUES('task_5_3_emdat',3);
INSERT INTO "user_state_task" VALUES('task_1_4_emdat',4);
INSERT INTO "user_state_task" VALUES('task_2_4_emdat',4);
INSERT INTO "user_state_task" VALUES('task_3_4_emdat',4);
INSERT INTO "user_state_task" VALUES('task_4_4_emdat',4);
INSERT INTO "user_state_task" VALUES('task_5_4_emdat',4);
INSERT INTO "user_state_task" VALUES('task_6_4_emdat',4);
INSERT INTO "user_state_task" VALUES('task_7_4_emdat',4);
INSERT INTO "user_state_task" VALUES('bad_type',1024);
INSERT INTO "user_state_task" VALUES('task_2_2_emdat',2);
CREATE TABLE vis_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
INSERT INTO "vis_fix" VALUES(5,1531957529246589,1531957529463080,216491);
INSERT INTO "vis_fix" VALUES(6,1531957529479686,1531957529737827,258141);
INSERT INTO "vis_fix" VALUES(8,1531957580131056,1531957580297530,166474);
INSERT INTO "vis_fix" VALUES(9,1531957593095774,1531957593545470,449696);
COMMIT;
