use bouncer;
revoke all privileges on bouncer.* from `bounceradmin`@`%`;
grant SELECT,INSERT,UPDATE,DELETE ON mirror_os TO `bounceradmin`@`%`;
grant SELECT,INSERT,UPDATE,DELETE ON mirror_locations TO `bounceradmin`@`%`;
grant SELECT,INSERT,UPDATE,DELETE ON mirror_products TO `bounceradmin`@`%`;
grant SELECT,INSERT,UPDATE,DELETE ON mirror_product_langs TO `bounceradmin`@`%`;
grant SELECT,INSERT,UPDATE,DELETE ON mirror_aliases TO `bounceradmin`@`%`;
flush privileges;
