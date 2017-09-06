Command Reference
=================



These commands will help you get started with stable.world

.. click:: stable_world.script:main
   :prog: stable.world


CI Integration
-----------------------

Experimental

.. click:: stable_world.commands.ci:ci_circle
   :prog: stable.world ci:circle


.. click:: stable_world.commands.ci:ci_bash
   :prog: stable.world ci:bash


Authentication Commands
-----------------------


.. click:: stable_world.commands.auth:register
   :prog: stable.world register


.. click:: stable_world.commands.auth:login
   :prog: stable.world login


.. click:: stable_world.commands.auth:logout
   :prog: stable.world logout


.. click:: stable_world.commands.auth:token
   :prog: stable.world token


.. click:: stable_world.commands.auth:whoami
   :prog: stable.world whoami


Bucket Commands
----------------

These commands manipulate stable.world buckets


.. click:: stable_world.commands.bucket:bucket_list
   :prog: stable.world bucket:list


.. click:: stable_world.commands.bucket:bucket
   :prog: stable.world bucket


.. click:: stable_world.commands.bucket:bucket_cache_add
   :prog: stable.world bucket:cache:add


.. click:: stable_world.commands.bucket:bucket_cache_remove
   :prog: stable.world bucket:cache:remove


.. click:: stable_world.commands.bucket:bucket_create
   :prog: stable.world bucket:create


.. click:: stable_world.commands.bucket:bucket_destroy
   :prog: stable.world bucket:destroy

.. click:: stable_world.commands.bucket:bucket_freeze
   :prog: stable.world bucket:freeze

.. click:: stable_world.commands.bucket:bucket_unfreeze
   :prog: stable.world bucket:unfreeze

.. click:: stable_world.commands.bucket:bucket_objects
   :prog: stable.world bucket:objects

.. click:: stable_world.commands.bucket:bucket_rollback
   :prog: stable.world bucket:rollback


Configuration Commands
----------------------

These commands can be used in your build script

.. click:: stable_world.commands.execute:configure
   :prog: stable.world configure

.. click:: stable_world.commands.execute:configure_pip
   :prog: stable.world configure pip


Misc Commands
-------------


.. click:: stable_world.commands.misc:info
   :prog: stable.world info
