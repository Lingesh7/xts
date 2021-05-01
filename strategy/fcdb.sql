CREATE SEQUENCE "public".broker_id_seq START WITH 1;

CREATE SEQUENCE "public".customer_id_seq START WITH 1;

CREATE SEQUENCE "public".strategy_id_seq START WITH 501;

CREATE SEQUENCE "public".strategy_params_id_seq START WITH 1;

CREATE SEQUENCE "public".strategy_strategy_params_id_seq START WITH 1;

CREATE SEQUENCE "public".subscriber_id_seq START WITH 5000;

CREATE SEQUENCE "public".subscribers_customer_id_seq START WITH 1;

CREATE SEQUENCE "public".subscribers_id_seq START WITH 1;

CREATE SEQUENCE "public".subscribers_run_counter_seq START WITH 1;

CREATE SEQUENCE "public".user_id_seq START WITH 10000;

CREATE  TABLE "public".broker (
    id                   integer DEFAULT nextval('broker_id_seq'::regclass) NOT NULL ,
    name                 varchar(100)  NOT NULL ,
    CONSTRAINT pk_broker_id PRIMARY KEY ( id )
 );

CREATE  TABLE "public".customer (
    id                   smallserial DEFAULT nextval('customer_id_seq'::regclass) NOT NULL ,
    first_name           varchar(100)   ,
    last_name            varchar(100)   ,
    mobile               bigint   ,
    mail                 varchar(50)   ,
    address              varchar(200)   ,
    active               boolean   ,
    telegram_id          integer   ,
    created_at           timestamp(22) DEFAULT CURRENT_TIMESTAMP  ,
    updated_at           timestamp(22) DEFAULT CURRENT_TIMESTAMP  ,
    CONSTRAINT pk_customer_id PRIMARY KEY ( id )
 );

CREATE  TABLE "public".strategy (
    id                   integer  NOT NULL ,
    name                 varchar(100)  NOT NULL ,
    min_multiplier       integer DEFAULT 1 NOT NULL ,
    capital_required     numeric(12,2)   ,
    price_per_month      numeric(10,2) DEFAULT 0 NOT NULL ,
    description          text DEFAULT 'FirstChoice Strategy'::text  ,
    strategy_params_id   integer DEFAULT nextval('strategy_strategy_params_id_seq'::regclass) NOT NULL ,
    created_at           timestamp(22) DEFAULT CURRENT_TIMESTAMP  ,
    updated_at           timestamp(22) DEFAULT CURRENT_TIMESTAMP  ,
    CONSTRAINT pk_strategy_id PRIMARY KEY ( id )
 );

CREATE  TABLE "public".strategy_params (
    id                   integer DEFAULT nextval('strategy_params_id_seq'::regclass) NOT NULL ,
    name                 varchar(100)  NOT NULL ,
    strategy_id          integer   ,
    script_name          varchar(100)   ,
    start_time           text[]   ,
    repair_time          time   ,
    end_time             time DEFAULT '15:05:00'::time without time zone  ,
    target               numeric(7,2)   ,
    stop_loss            numeric(7,2)   ,
    created_at           timestamp(22) DEFAULT CURRENT_TIMESTAMP  ,
    updated_at           timestamp(22) DEFAULT CURRENT_TIMESTAMP  ,
    CONSTRAINT pk_strategy_params_id PRIMARY KEY ( id ),
    CONSTRAINT fk_strategy_params_strategy FOREIGN KEY ( strategy_id ) REFERENCES "public".strategy( id )
 );

CREATE  TABLE "public".subscribers (
    id                   integer DEFAULT nextval('subscribers_id_seq'::regclass) NOT NULL ,
    customer_id          smallserial DEFAULT nextval('subscribers_customer_id_seq'::regclass) NOT NULL ,
    strategy_id          integer  NOT NULL ,
    broker_id            integer   ,
    run_counter          integer DEFAULT nextval('subscribers_run_counter_seq'::regclass) NOT NULL ,
    is_active            char(1)  NOT NULL ,
    start_date           date   ,
    end_date             date   ,
    created_at           timestamp(22) DEFAULT CURRENT_TIMESTAMP  ,
    updated_at           timestamp(22) DEFAULT CURRENT_TIMESTAMP  ,
    CONSTRAINT pk_subscribers_id PRIMARY KEY ( id ),
    CONSTRAINT fk_subscribers_customer FOREIGN KEY ( customer_id ) REFERENCES "public".customer( id )   ,
    CONSTRAINT fk_subscribers_strategy FOREIGN KEY ( strategy_id ) REFERENCES "public".strategy( id )   ,
    CONSTRAINT fk_subscribers_broker FOREIGN KEY ( broker_id ) REFERENCES "public".broker( id )
 );

CREATE OR REPLACE FUNCTION public.trigger_set_timestamp()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$function$
;

CREATE TRIGGER set_timestamp BEFORE UPDATE ON public.customer FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp BEFORE UPDATE ON public.strategy_params FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp BEFORE UPDATE ON public.strategy FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp BEFORE UPDATE ON public.subscribers FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();

INSERT INTO "public".broker( id, name ) VALUES ( 1, 'IIFL');
INSERT INTO "public".broker( id, name ) VALUES ( 2, 'Alice Blue');
INSERT INTO "public".customer( id, first_name, last_name, mobile, mail, address, active, telegram_id, created_at, updated_at ) VALUES ( 10000, 'Linges', 'M', 6382860148, 'nerus.q8@gmail.com', 'Chennai', null, null, '2021-04-29 10.35.55 PM', '2021-04-29 10.36.23 PM');
INSERT INTO "public".customer( id, first_name, last_name, mobile, mail, address, active, telegram_id, created_at, updated_at ) VALUES ( 10001, 'Raja', 'YOGI', 9884411611, 'acumeraja@yahoo.co.in', 'Cbe', null, null, '2021-04-29 10.35.55 PM', '2021-04-29 10.36.23 PM');
INSERT INTO "public".strategy( id, name, min_multiplier, capital_required, price_per_month, description, strategy_params_id, created_at, updated_at ) VALUES ( 501, 'Option Scalper', 1, 50000, 500, 'BUY 1 lot CE and PE at the same time.', 3, '2021-04-30 12.33.31 AM', '2021-04-30 12.33.31 AM');
INSERT INTO "public".strategy( id, name, min_multiplier, capital_required, price_per_month, description, strategy_params_id, created_at, updated_at ) VALUES ( 500, 'NFO Panther', 1, 150000, 1000, 'BUY 2 lots and SELL 1 lot at SL, Same cont for every 1 hour', 2, '2021-04-29 10.46.49 PM', '2021-04-30 12.48.54 AM');
INSERT INTO "public".strategy_params( id, name, strategy_id, script_name, start_time, repair_time, end_time, target, stop_loss, created_at, updated_at ) VALUES ( 12, 'os_params', 501, 'NFO_Panther_Live', '{09:45:00}', '14:40:00', '15:05:00', 3000, -1500, '2021-04-30 12.46.41 AM', '2021-04-30 12.46.41 AM');
INSERT INTO "public".strategy_params( id, name, strategy_id, script_name, start_time, repair_time, end_time, target, stop_loss, created_at, updated_at ) VALUES ( 13, 'nfo_params', 500, 'NFO_Panther_Live', '{09:30:00,10:00:00}', '14:40:00', '15:05:00', 24000, -12000, '2021-04-30 12.46.41 AM', '2021-04-30 12.46.41 AM');
INSERT INTO "public".subscribers( id, customer_id, strategy_id, run_counter, is_active, start_date, end_date, created_at, updated_at, broker_id ) VALUES ( 5003, 10000, 500, 3, 'Y', '2021-04-29', '2021-05-29', '2021-04-29 10.52.00 PM', '2021-04-29 10.52.00 PM', null);
