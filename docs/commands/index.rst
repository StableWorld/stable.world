Command Reference
=================



These commands will help you get started with stable.world

.. click:: stable_world.script:main
   :prog: stable.world


CI Integration
-----------------------

Experimental

.. click:: stable_world.script:ci_circle
   :prog: stable.world ci:circle


.. click:: stable_world.script:ci_bash
   :prog: stable.world ci:bash


Authentication Commands
-----------------------


.. click:: stable_world.script:register
   :prog: stable.world register


.. click:: stable_world.script:login
   :prog: stable.world login


.. click:: stable_world.script:logout
   :prog: stable.world logout


.. click:: stable_world.script:token
   :prog: stable.world token


.. click:: stable_world.script:whoami
   :prog: stable.world whoami


Bucket Commands
----------------

These commands manipulate stable.world buckets


.. click:: stable_world.script:bucket_list
   :prog: stable.world bucket:list


.. click:: stable_world.script:bucket
   :prog: stable.world bucket


.. click:: stable_world.script:bucket_cache_add
   :prog: stable.world bucket:cache:add


.. click:: stable_world.script:bucket_cache_remove
   :prog: stable.world bucket:cache:remove


.. click:: stable_world.script:bucket_create
   :prog: stable.world bucket:create


.. click:: stable_world.script:bucket_destroy
   :prog: stable.world bucket:destroy

.. click:: stable_world.script:bucket_freeze
   :prog: stable.world bucket:freeze

.. click:: stable_world.script:bucket_unfreeze
   :prog: stable.world bucket:unfreeze

.. click:: stable_world.script:bucket_objects
   :prog: stable.world bucket:objects

.. click:: stable_world.script:bucket_rollback
   :prog: stable.world bucket:rollback


Configuration Commands
----------------------

These commands can be used in your build script

.. click:: stable_world.script:configure
   :prog: stable.world configure

.. click:: stable_world.script:configure_pip
   :prog: stable.world configure pip


Misc Commands
-------------


.. click:: stable_world.script:info
   :prog: stable.world info
