#ifndef FLS_H
#define FLS_H

#include "Std_Types.h"
#include "MemIf_Types.h"

typedef uint32 Fls_AddressType;
typedef uint32  Fls_LengthType;


typedef struct STag_Fls_SfDdrPatternConfigType
{
  /* ulPatternAddress */
  uint32 ulPatternAddress;

  /* ulPatternValue */
  uint32 ulPatternValue;

  /* ulNumberOfPattern */
  uint32 ulNumberOfPattern;
} Fls_SfDdrPatternConfigType;

typedef struct STag_Fls_ConfigType
{
  /* Database start value - 0x0ED70100UL */
  uint32 ulStartOfDbToc;
  /* TRACE [R4, SWS_Fls_00109] */
  /* TRACE [R4, SWS_Fls_00110] */
  /* Pointer to job end callback notification */
  P2FUNC (void, FLS_CODE, pJobEndNotificationPointer)(void);
  /* Pointer to job error callback notification */
  P2FUNC (void, FLS_CODE, pJobErrorNotificationPointer)(void);
  /* TRACE [R4, SWS_Fls_00248] */
  /* Enumeration to store Fls Default Mode */
  MemIf_ModeType enFlsDefaultMode;
  /* The maximum number of bytes to read or compare in one cycle of
   * the flash driver's job processing function in fast mode.
   */
  uint32 ulFlsMaxFastReadBytes;
  /* The maximum number of bytes to read or compare in one cycle of
   * the flash driver's job processing function in normal mode.
   */
  uint32 ulFlsMaxSlowReadBytes;
  uint32 ulFlsMaxWriteBytes;
  /* Variable to store the Fls Protection value in bytes */
  uint32 ulFlsProtection;
  /* TRACE [R4, SWS_Fls_00355] */
  /* The number of Sector Partition  */
  uint32 ulNumberOfSectorPartition;
  /* Index of Sector Partition on the constant structure Fls_SectorMap */
  uint32 ulSectorPartitionIndex;
} Fls_ConfigType;

/* Error codes */
#define FLS_E_OK        0x00
#define FLS_E_NOT_OK    0x01
#define FLS_E_BUSY      0x02
#define FLS_E_PARAM     0x03
#define FLS_E_UNINIT    0x04

/* Function prototypes */
Std_ReturnType Fls_Init(const Fls_ConfigType* ConfigPtr);
Std_ReturnType Fls_Write(uint32 FlsAddr, const uint8 *DataBufferPtr, uint32 Length);
Std_ReturnType Fls_Erase(uint32 FlsAddr, uint32 Length);
MemIf_StatusType Fls_GetStatus(void);
void Fls_JobEndNotification(void);
void Fls_JobErrorNotification(void);
FUNC(MemIf_JobResultType, FLS_CODE) Fls_GetJobResult(void);
FUNC(void, FLS_CODE) Fls_Cancel(void);
FUNC(Std_ReturnType, FLS_CODE) Fls_Read
  (Fls_AddressType SourceAddress,
  CONSTP2VAR(uint8, AUTOMATIC, FLS_CODE) TargetAddressPtr,
  Fls_LengthType Length);
FUNC(void, FLS_CODE) Fls_SetMode(MemIf_ModeType Mode);
void Fls_MainFunction(void);

extern const Fls_ConfigType FlsConfigSet_0;


#endif /* FLS_H */
