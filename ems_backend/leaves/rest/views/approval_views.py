from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from leaves.models import LeaveRequest
from leaves.services import process_leave_approval, withdraw_leave
from core.choices import Status, LeaveStatus, ApprovalType, Decision

@api_view(['POST'])
def approve_leave(request, pk):
    # View to approve/reject leave
    try:
        leave_request = LeaveRequest.objects.get(id=pk, status=Status.ACTIVE)
        approval_type = request.data.get('approval_type')
        decision = request.data.get('decision')
        notes = request.data.get('notes', '')
        
        # Validate required fields
        if not approval_type or not decision:
            return Response({'error': 'approval_type and decision are required'}, status=400)
        
        # Convert string to enum
        try:
            approval_type = ApprovalType(approval_type)
            decision = Decision(decision)
        except ValueError:
            return Response({'error': 'Invalid approval_type or decision'}, status=400)
        
        # Permission checks 
        if approval_type == ApprovalType.TEAM_LEAD:
            if request.user.role.name != 'Team Lead':
                return Response({'error': 'Only Team Leads can approve as team lead'}, status=403)
            if leave_request.employee.team != request.user.team:
                return Response({'error': 'Can only approve leaves for your team'}, status=403)
            if leave_request.employee == request.user:
                return Response({'error': 'Cannot approve your own leave'}, status=403)
        
        elif approval_type == ApprovalType.HR:
            if request.user.role.name != 'HR':
                return Response({'error': 'Only HR can give final approval'}, status=403)
        
        # Process approval
        approval = process_leave_approval(leave_request, request.user, approval_type, decision, notes)
        
        return Response({
            'message': f'Leave {decision.lower()}ed successfully',
            'leave_status': leave_request.leave_status,
            'approval_id': approval.id
        }, status=status.HTTP_200_OK)
        
    except LeaveRequest.DoesNotExist:
        return Response({'error': 'Leave request not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def withdraw_leave_view(request, pk):
    # Simple view for HR to withdraw leave 
    try:
        leave_request = LeaveRequest.objects.get(id=pk, status=Status.ACTIVE)
        
        # Permission check 
        if request.user.role.name != 'HR':
            return Response({'error': 'Only HR can withdraw leaves'}, status=403)
        
        if leave_request.leave_status != LeaveStatus.HR_APPROVED:
            return Response({'error': 'Only HR-approved leaves can be withdrawn'}, status=400)
        
        notes = request.data.get('notes', '')
        approval = withdraw_leave(leave_request, request.user, notes)
        
        return Response({
            'message': 'Leave withdrawn successfully',
            'leave_status': leave_request.leave_status,
            'approval_id': approval.id
        }, status=status.HTTP_200_OK)
        
    except LeaveRequest.DoesNotExist:
        return Response({'error': 'Leave request not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)