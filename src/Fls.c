#include "Fls.h"
#include "vIO.h"
#include <stdio.h>
#include <stddef.h>

/* Global variables */
static MemIf_StatusType Fls_Status = MEMIF_IDLE;

/* Function definitions */
Std_ReturnType Fls_Init(const Fls_ConfigType* ConfigPtr)
{
    /* Initialize flash driver */
    /* Return FLS_E_OK if successful, FLS_E_NOT_OK otherwise */
    
    printf("Fls Init.\n");
    
    if (vFls_Init != NULL)
        vFls_Init(); /* all params are known in python from metamodel */
        
    return FLS_E_OK;
}

Std_ReturnType Fls_Write(uint32 FlsAddr, const uint8 *DataBufferPtr, uint32 Length)
{
    Fls_Status = FLS_E_OK;
    /* Write data to flash */
    /* Return FLS_E_OK if successful, FLS_E_NOT_OK otherwise */
    
    printf("Fls_Write %x, %d, %d\n", FlsAddr, *DataBufferPtr,  Length);
    
    if (vFls_Write != NULL)
        Fls_Status = vFls_Write(FlsAddr, *DataBufferPtr);
    
    return Fls_Status;
}

Std_ReturnType Fls_Erase(uint32 FlsAddr, uint32 Length)
{
    Fls_Status = FLS_E_OK;


    /* Erase flash memory */
    /* Return FLS_E_OK if successful, FLS_E_NOT_OK otherwise */
    if (vFls_Erase != NULL)
        Fls_Status = vFls_Erase(FlsAddr, Length);

    return Fls_Status;
}

MemIf_StatusType Fls_GetStatus(void)
{
    MemIf_StatusType status = MEMIF_IDLE;

    if (vFls_GetStatus != NULL)
        status = vFls_GetStatus();

    /* Return status of flash driver */
    return status;
}


void Fls_JobEndNotification(void)
{
    printf("Fls_JobEndNotification \n");
}

void Fls_JobErrorNotification(void){
    
}
FUNC(MemIf_JobResultType, FLS_CODE) Fls_GetJobResult(void)
{
    MemIf_JobResultType status = MEMIF_JOB_OK;

    if (vFls_GetJobResult != NULL)
        status = vFls_GetJobResult();
    
    return status;
}
FUNC(void, FLS_CODE) Fls_Cancel(void)
{
    if (vFls_Cancel != NULL)
        vFls_Cancel();    
}

FUNC(Std_ReturnType, FLS_CODE) Fls_Read(Fls_AddressType SourceAddress,
                                        CONSTP2VAR(uint8, AUTOMATIC, FLS_CODE) TargetAddressPtr,
                                        Fls_LengthType Length)
{
    Fls_Status = FLS_E_OK;

    if (vFls_Read != NULL)
        Fls_Status = vFls_Read(SourceAddress, TargetAddressPtr, Length);
    
    return Fls_Status;
}

FUNC(void, FLS_CODE) Fls_SetMode(MemIf_ModeType Mode)
{
    if (vFls_SetMode != NULL)
        vFls_SetMode(Mode);    
}

void Fls_MainFunction(void)
{
}

/* Define Fls configuration structure */
const Fls_ConfigType FlsConfigSet_0 = {
    /* Database start value - 0x0ED70100UL */
    .ulStartOfDbToc = 0x0ED70100UL,
    /* Pointer to job end callback notification */
    .pJobEndNotificationPointer = &Fls_JobEndNotification,
    /* Pointer to job error callback notification */
    .pJobErrorNotificationPointer = &Fls_JobErrorNotification,
    /* Enumeration to store Fls Default Mode */
    .enFlsDefaultMode = MEMIF_MODE_SLOW,
    /* The maximum number of bytes to read or compare in one cycle of
     * the flash driver's job processing function in fast mode.
     */
    .ulFlsMaxFastReadBytes = 256U,
    /* The maximum number of bytes to read or compare in one cycle of
     * the flash driver's job processing function in normal mode.
     */
    .ulFlsMaxSlowReadBytes = 128U,
    /* The maximum number of bytes to write in one cycle of the flash driver's
     * job processing function.
     */
    .ulFlsMaxWriteBytes = 32U,
    /* Variable to store the Fls Protection value in bytes */
    .ulFlsProtection = 256U,
    /* The number of Sector Partition  */
    .ulNumberOfSectorPartition = 4U,
    /* Index of Sector Partition on the constant structure Fls_SectorMap */
    .ulSectorPartitionIndex = 2U,
};
