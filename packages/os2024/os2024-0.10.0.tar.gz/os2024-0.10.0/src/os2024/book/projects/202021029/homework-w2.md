# Week 2 Homework

## 질문 1

- 다음 플래그와 함께 process-run.py를 실행하세요: -l 5:100,5:100. CPU 활용률(예: CPU가 사용 중인 시간의 백분율)은 어떻게 되어야 할까요? 왜 그렇게 알 수 있나요? -c와 -p 플래그를 사용해 여러분의 생각이 맞는지 확인해 보세요.

### 답변 1

- CPU 활용률은 100%이다. -c 플래그와 -p 플래그를 실행해 확인해 본 결과, 각 프로세스가 CPU에서 실행 중이고, CPU가 사용 중인 시간이 전체 실행 시간 중 100%라는 사실을 알 수 있었다.

```
➜ ./process-run.py -l 5:100,5:100 -c -p
Time        PID: 0        PID: 1           CPU           IOs
  1        RUN:cpu         READY             1
  2        RUN:cpu         READY             1
  3        RUN:cpu         READY             1
  4        RUN:cpu         READY             1
  5        RUN:cpu         READY             1
  6           DONE       RUN:cpu             1
  7           DONE       RUN:cpu             1
  8           DONE       RUN:cpu             1
  9           DONE       RUN:cpu             1
 10           DONE       RUN:cpu             1

Stats: Total Time 10
Stats: CPU Busy 10 (100.00%)
Stats: IO Busy  0 (0.00%)
```

## 질문 2

- 이제 다음 플래그로 실행해 보세요: ./process-run.py -l 4:100,1:0. 이 플래그는 4개의 명령어(모두 CPU 사용)를 가진 하나의 프로세스와 I/O를 실행하고 완료될 때까지 기다리는 하나의 프로세스를 지정합니다. 두 프로세스를 모두 완료하는 데 얼마나 걸리나요? -c와 -p를 사용해 여러분의 생각이 맞는지 확인해 보세요.

### 답변 2

- 첫번쨰 프로세스의 CPU 실행 시간 4단계와 두 번째 프로세스의 CPU 실행 시간 1단계를 합쳐서 총 5단계이며, 총 11이다.

```
➜ ./process-run.py -l 4:100,1:0 -c -p
Time        PID: 0        PID: 1           CPU           IOs
  1        RUN:cpu         READY             1
  2        RUN:cpu         READY             1
  3        RUN:cpu         READY             1
  4        RUN:cpu         READY             1
  5           DONE        RUN:io             1
  6           DONE       BLOCKED                           1
  7           DONE       BLOCKED                           1
  8           DONE       BLOCKED                           1
  9           DONE       BLOCKED                           1
 10           DONE       BLOCKED                           1
 11*          DONE   RUN:io_done             1

Stats: Total Time 11
Stats: CPU Busy 6 (54.55%)
Stats: IO Busy  5 (45.45%)
```

## 질문 3

- 프로세스의 순서를 바꿔 보세요: -l 1:0,4:100. 이제 어떻게 되나요? 순서를 바꾸는 것이 중요한가요? 왜 그런가요? (항상 그렇듯이 -c와 -p를 사용해 여러분의 생각이 맞는지 확인해 보세요)

### 답변 3

- 순서를 바꾸니 총 실행 시간이 11에서 7로 줄어들었고, CPU와 IO 사용률도 바뀌었다. 이것으로 프로세스의 순서를 바꾸는 것은 시스템 성능과 효율성에 영향을 끼친다는 것을 알 수 있다.

```
➜ ./process-run.py -l 1:0,4:100 -c -p
Time        PID: 0        PID: 1           CPU           IOs
  1         RUN:io         READY             1
  2        BLOCKED       RUN:cpu             1             1
  3        BLOCKED       RUN:cpu             1             1
  4        BLOCKED       RUN:cpu             1             1
  5        BLOCKED       RUN:cpu             1             1
  6        BLOCKED          DONE                           1
  7*   RUN:io_done          DONE             1

Stats: Total Time 7
Stats: CPU Busy 6 (85.71%)
Stats: IO Busy  5 (71.43%)
```

## 질문 4

- 이제 다른 플래그들을 살펴보겠습니다. 중요한 플래그 중 하나는 -S인데, 이는 프로세스가 I/O를 실행할 때 시스템이 어떻게 반응하는지 결정합니다. 플래그를 SWITCH_ON_END로 설정하면 한 프로세스가 I/O를 수행하는 동안 시스템은 다른 프로세스로 전환하지 않고 해당 프로세스가 완전히 끝날 때까지 기다립니다. 다음 두 프로세스를 실행할 때 어떤 일이 일어나나요(-l 1:0,4:100 -c -S SWITCH_ON_END), 하나는 I/O를 수행하고 다른 하나는 CPU 작업을 수행합니다?

### 답변 4

- 프로세스 0이 CPU 작업을 수행하는 동안, 프로세스 1은 대기 상태에 있다. 프로세스 0의 I/O 작업이 완료된 후에야 프로세스 1의 CPU 작업을 수행한다.

```
➜ ./process-run.py -l 1:0,4:100 -c -S SWITCH_ON_END
Time        PID: 0        PID: 1           CPU           IOs
  1         RUN:io         READY             1
  2        BLOCKED         READY                           1
  3        BLOCKED         READY                           1
  4        BLOCKED         READY                           1
  5        BLOCKED         READY                           1
  6        BLOCKED         READY                           1
  7*   RUN:io_done         READY             1
  8           DONE       RUN:cpu             1
  9           DONE       RUN:cpu             1
 10           DONE       RUN:cpu             1
 11           DONE       RUN:cpu             1
```

## 질문 5

- 이제 같은 프로세스를 실행하되, 한 프로세스가 I/O를 기다리는(WAITING) 동안 다른 프로세스로 전환되도록 switching 동작을 설정해 봅시다(-l 1:0,4:100 -c -S SWITCH_ON_IO). 이제 어떤 일이 일어나나요? -c와 -p를 사용해 여러분의 생각이 맞는지 확인해 보세요.

### 답변 5

- 프로세스 0이 I/O를 실행하는 동안 시스템은 다른 프로세스로 전환된다. 그래서 프로세스1 CPU 작업을 수행할 수 있다. 이후, 프로세스 0의 I/O가 완료되면 프로세스 1이 다시 CPU를 할당받아 실행한다. 이렇게 두 프로세스가 번갈아가며 실행되며, 하나가 I/O를 기다리는 동안에도 다른 하나가 CPU 작업을 수행할 수 있다. 이로 인해 시스템의 자원이 효율적으로 활용되며, 대기 시간이 최소화되었다.

```
➜ ./process-run.py -l 1:0,4:100 -c -p -S SWITCH_ON_IO
Time        PID: 0        PID: 1           CPU           IOs
  1         RUN:io         READY             1
  2        BLOCKED       RUN:cpu             1             1
  3        BLOCKED       RUN:cpu             1             1
  4        BLOCKED       RUN:cpu             1             1
  5        BLOCKED       RUN:cpu             1             1
  6        BLOCKED          DONE                           1
  7*   RUN:io_done          DONE             1

Stats: Total Time 7
Stats: CPU Busy 6 (85.71%)
Stats: IO Busy  5 (71.43%)
```

## 질문 6

- 또 다른 중요한 동작은 I/O가 완료될 때 수행할 작업입니다. -I IO_RUN_LATER를 사용하면 I/O가 완료될 때 그것을 실행한 프로세스가 반드시 즉시 실행되는 것은 아닙니다. 오히려 그 시점에 실행 중이던 프로세스가 계속 실행됩니다. 이러한 프로세스 조합을 실행하면 어떤 일이 일어나나요? (./process-run.py -l 3:0,5:100,5:100,5:100 -S SWITCH_ON_IO -I IO_RUN_LATER -c -p) 시스템 자원이 효율적으로 활용되고 있나요?

### 답변 6

- 시스템 자원이 효율적으로 활용되고 있지 않다. 프로세스가 I/O를 수행하는 동안에도 CPU는 유휴 상태에 있고, 그 반대에도 유사한 패턴이 반복되었다. 이건 프로세스가 I/O가 완료될 때까지 다른 프로세스로 전환되지 않고 기다리는 동안에도 시스템의 자원이 효율적으로 활용되지 않음을 보여준다. 이러한 동작은 시스템의 처리량과 응답 시간을 저하시킬 수 있다.

```
➜ ./process-run.py -l 3:0,5:100,5:100,5:100 -S SWITCH_ON_IO -I IO_RUN_LATER -c -p
Time        PID: 0        PID: 1        PID: 2        PID: 3           CPU           IOs
  1         RUN:io         READY         READY         READY             1
  2        BLOCKED       RUN:cpu         READY         READY             1             1
  3        BLOCKED       RUN:cpu         READY         READY             1             1
  4        BLOCKED       RUN:cpu         READY         READY             1             1
  5        BLOCKED       RUN:cpu         READY         READY             1             1
  6        BLOCKED       RUN:cpu         READY         READY             1             1
  7*         READY          DONE       RUN:cpu         READY             1
  8          READY          DONE       RUN:cpu         READY             1
  9          READY          DONE       RUN:cpu         READY             1
 10          READY          DONE       RUN:cpu         READY             1
 11          READY          DONE       RUN:cpu         READY             1
 12          READY          DONE          DONE       RUN:cpu             1
 13          READY          DONE          DONE       RUN:cpu             1
 14          READY          DONE          DONE       RUN:cpu             1
 15          READY          DONE          DONE       RUN:cpu             1
 16          READY          DONE          DONE       RUN:cpu             1
 17    RUN:io_done          DONE          DONE          DONE             1
 18         RUN:io          DONE          DONE          DONE             1
 19        BLOCKED          DONE          DONE          DONE                           1
 20        BLOCKED          DONE          DONE          DONE                           1
 21        BLOCKED          DONE          DONE          DONE                           1
 22        BLOCKED          DONE          DONE          DONE                           1
 23        BLOCKED          DONE          DONE          DONE                           1
 24*   RUN:io_done          DONE          DONE          DONE             1
 25         RUN:io          DONE          DONE          DONE             1
 26        BLOCKED          DONE          DONE          DONE                           1
 27        BLOCKED          DONE          DONE          DONE                           1
 28        BLOCKED          DONE          DONE          DONE                           1
 29        BLOCKED          DONE          DONE          DONE                           1
 30        BLOCKED          DONE          DONE          DONE                           1
 31*   RUN:io_done          DONE          DONE          DONE             1

Stats: Total Time 31
Stats: CPU Busy 21 (67.74%)
Stats: IO Busy  15 (48.39%)
```

## 질문 7

- 이제 같은 프로세스를 실행하되, -I IO_RUN_IMMEDIATE를 설정해 I/O를 실행한 프로세스를 즉시 실행하도록 해 봅시다. 이 동작은 어떻게 다른가요? 방금 I/O를 완료한 프로세스를 다시 실행하는 것이 왜 좋은 생각일 수 있을까요?

### 답변 7

- 프로세스 0이 처음에 I/O 작업을 수행한다. 시스템이 I/O를 기다리는 동안 CPU 작업이 가능한 다른 프로세스를 실행할 수 있도록 한다. 따라서 프로세스 1, 2, 3은 모두 CPU 작업을 수행할 수 있는 상태인 READY 상태로 대기한다. 프로세스 1은 CPU 작업을 수행한 후 BLOCKED 상태로 I/O를 기다린다. 프로세스 2와 3도 순차적으로 CPU 작업을 수행한 후 BLOCKED 상태로 대기한다. 프로세스 0이 I/O 작업을 완료하면, 이를 알리기 위해 RUN 상태로 전환된다. 이 때, -I IO_RUN_IMMEDIATE 플래그를 사용하면 프로세스 0은 즉시 CPU 작업을 수행할 수 있다. 그래서 프로세스 0은 즉시 CPU 작업을 시작하고, 이후에 BLOCKED 상태로 전환된다. 프로세스 1이 BLOCKED 상태에서 빠져나와 CPU 작업을 수행하고, 이어서 BLOCKED 상태로 전환된다. 이런 식으로 프로세스 2와 3도 CPU 작업을 번갈아가며 수행한다. 이러한 방식으로 각 프로세스가 번갈아 가며 CPU 작업을 수행하고, I/O 작업이 완료되는 즉시 CPU를 사용할 수 있기 때문에 시스템 자원이 효율적으로 활용된다.

```
➜ ./process-run.py -l 3:0,5:100,5:100,5:100 -I IO_RUN_IMMEDIATE -c -p
Time        PID: 0        PID: 1        PID: 2        PID: 3           CPU           IOs
  1         RUN:io         READY         READY         READY             1
  2        BLOCKED       RUN:cpu         READY         READY             1             1
  3        BLOCKED       RUN:cpu         READY         READY             1             1
  4        BLOCKED       RUN:cpu         READY         READY             1             1
  5        BLOCKED       RUN:cpu         READY         READY             1             1
  6        BLOCKED       RUN:cpu         READY         READY             1             1
  7*   RUN:io_done          DONE         READY         READY             1
  8         RUN:io          DONE         READY         READY             1
  9        BLOCKED          DONE       RUN:cpu         READY             1             1
 10        BLOCKED          DONE       RUN:cpu         READY             1             1
 11        BLOCKED          DONE       RUN:cpu         READY             1             1
 12        BLOCKED          DONE       RUN:cpu         READY             1             1
 13        BLOCKED          DONE       RUN:cpu         READY             1             1
 14*   RUN:io_done          DONE          DONE         READY             1
 15         RUN:io          DONE          DONE         READY             1
 16        BLOCKED          DONE          DONE       RUN:cpu             1             1
 17        BLOCKED          DONE          DONE       RUN:cpu             1             1
 18        BLOCKED          DONE          DONE       RUN:cpu             1             1
 19        BLOCKED          DONE          DONE       RUN:cpu             1             1
 20        BLOCKED          DONE          DONE       RUN:cpu             1             1
 21*   RUN:io_done          DONE          DONE          DONE             1

Stats: Total Time 21
Stats: CPU Busy 21 (100.00%)
Stats: IO Busy  15 (71.43%)
```

## 질문 8

- 이제 무작위로 생성된 프로세스로 실행해 봅시다: -s 1 -l 3:50,3:50 또는 -s 2 -l 3:50,3:50 또는 -s 3 -l 3:50,3:50. 추적 결과가 어떻게 될지 예측해 보세요. -I IO_RUN_IMMEDIATE 플래그와 -I IO_RUN_LATER 플래그를 사용할 때 어떤 일이 일어나나요? -S SWITCH_ON_IO와 -S SWITCH_ON_END를 사용할 때 어떤 일이 일어나나요?

### 답변 8

- '-I IO_RUN_LATER' 플래그 대신 '-I IO_RUN_IMMEDIATE' 플래그를 쓰면 I/O 작업이 끝난 프로세스가 즉시 CPU에서 실행된다. 그래서 자원을 좀 더 효율적으로 사용할 수 있고, 전체 작업 완료 시간이 짧아진다.

- '-S SWITCH_ON_END' 플래그 대신 '-S SWITCH_ON_IO' 플래그를 쓰면 프로세스가 I/O를 시작하면 즉시 다른 프로세스로 전환된다. 자원을 좀 더 효율적으로 사용할 수 있고, 특히 다수의 프로세스 환경에서 사용하면 좋다. 반면 프로세스가 적은 경우에는 '-S SWITCH_ON_END'가 적합할 수 있다.

- 결론을 말하자면 효율적인 자원 사용과 빠른 작업을 위해서는 '-I IO_RUN_IMMEDIATE'와 '-S SWITCH_ON_IO'를 사용하는 것이 좋다.
