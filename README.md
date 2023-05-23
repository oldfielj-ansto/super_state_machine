Super State Machine
===================

[![PyPI version shields.io](https://img.shields.io/pypi/v/super_state_machine.svg)](https://pypi.python.org/pypi/super_state_machine)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/super_state_machine)](https://pypi.python.org/pypi/super_state_machine)
[![GitHub license](https://img.shields.io/github/license/beregond/super_state_machine.svg)](https://github.com/beregond/super_state_machine/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/beregond/super_state_machine.svg?style=social&label=Star&maxAge=2592000)](https://GitHub.com/beregond/super_state_machine/stargazers/)

Super State Machine gives you utilities to build finite state machines.

- Free software: BSD license
- Documentation: [https://super_state_machine.readthedocs.org](https://super_state_machine.readthedocs.org)
- Source: [https://github.com/beregond/super_state_machine](https://github.com/beregond/super_state_machine)

Features
--------

- Fully tested with Python 3.8, 3.9, 3.10, 3.11 and PyPi.
- Create finite state machines:

  ```python
  >>> from enum import Enum

  >>> from super_state_machine import machines


  >>> class Task(machines.StateMachine):
  ...
  ...    state = 'draft'
  ...
  ...    class States(Enum):
  ...
  ...         DRAFT = 'draft'
  ...         SCHEDULED = 'scheduled'
  ...         PROCESSING = 'processing'
  ...         SENT = 'sent'
  ...         FAILED = 'failed'

  >>> task = Task()
  >>> task.is_draft
  False
  >>> task.set_draft()
  >>> task.state
  'draft'
  >>> task.state = 'scheduled'
  >>> task.is_scheduled
  True
  >>> task.state = 'process'
  >>> task.state
  'processing'
  >>> task.state = 'wrong'
  *** ValueError: Unrecognized value ('wrong').
  ```

- Define allowed transitions graph, define additional named transitions and checkers:

  ```python
  >>> class Task(machines.StateMachine):
  ...
  ...     class States(Enum):
  ...
  ...         DRAFT = 'draft'
  ...         SCHEDULED = 'scheduled'
  ...         PROCESSING = 'processing'
  ...         SENT = 'sent'
  ...         FAILED = 'failed'
  ...
  ...     class Meta:
  ...
  ...         allow_empty = False
  ...         initial_state = 'draft'
  ...         transitions = {
  ...             'draft': ['scheduled', 'failed'],
  ...             'scheduled': ['failed'],
  ...             'processing': ['sent', 'failed']
  ...         }
  ...         named_transitions = [
  ...             ('process', 'processing', ['scheduled']),
  ...             ('fail', 'failed')
  ...         ]
  ...         named_checkers = [
  ...             ('can_be_processed', 'processing'),
  ...         ]
  >>> task = Task()
  >>> task.state
  'draft'
  >>> task.process()
  *** TransitionError: Cannot transit from 'draft' to 'processing'.
  >>> task.set_scheduled()
  >>> task.can_be_processed
  True
  >>> task.process()
  >>> task.state
  'processing'
  >>> task.fail()
  >>> task.state
  'failed'
  ```

  Note, that third argument restricts from which states transition will be
  **added** to allowed (in case of `process`, new allowed transition will be
  added, from 'scheduled' to 'processing'). No argument means all available
  states, `None` or empty list won't add anything beyond defined ones.

- Use state machines as properties:

  ```python
  >>> from enum import Enum

  >>> from super_state_machine import machines, extras


  >>> class Lock(machine.StateMachine):

  ...     class States(Enum):
  ...
  ...         OPEN = 'open'
  ...         LOCKED = 'locked'
  ...
  ...     class Meta:
  ...
  ...         allow_empty = False
  ...         initial_state = 'locked'
  ...         named_transitions = [
  ...             ('open', 'open'),
  ...             ('lock', 'locked'),
  ...         ]


  >>> class Safe(object):
  ...
  ...     lock1 = extras.PropertyMachine(Lock)
  ...     lock2 = extras.PropertyMachine(Lock)
  ...     lock3 = extras.PropertyMachine(Lock)
  ...
  ...     locks = ['lock1', 'lock2', 'lock3']
  ...
  ...     def is_locked(self):
  ...          locks = [getattr(self, lock).is_locked for lock in self.locks]
  ...          return any(locks)
  ...
  ...     def is_open(self):
  ...         locks = [getattr(self, lock).is_open for lock in self.locks]
  ...         return all(locks)

  >>> safe = Safe()
  >>> safe.lock1
  'locked'
  >>> safe.is_open
  False
  >>> safe.lock1.open()
  >>> safe.lock1.is_open
  True
  >>> safe.lock1
  'open'
  >>> safe.is_open
  False
  >>> safe.lock2.open()
  >>> safe.lock3 = 'open'
  >>> safe.is_open
  True
  ```
