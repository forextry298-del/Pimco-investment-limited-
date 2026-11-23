function notifyUser(msg){alert(msg)}
function closeModal(id){const el=document.getElementById(id);if(el)el.classList.remove('show')}
document.querySelectorAll('[data-tab]').forEach(btn=>btn.addEventListener('click',()=>{
 document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('active',b===btn));
 document.querySelectorAll('#register,#login').forEach(f=>f.classList.toggle('hidden',f.id!==btn.dataset.tab));
}));
const requestedTab=new URLSearchParams(window.location.search).get('tab');
if(requestedTab==='login'){
 const loginTab=document.querySelector('[data-tab="login"]');
 if(loginTab)loginTab.click();
}
document.querySelectorAll('[data-open]').forEach(btn=>btn.addEventListener('click',()=>{
 const kind=btn.dataset.open, modal=document.getElementById('transactionModal');
 if(!modal)return;
 document.getElementById('transactionKind').value=kind;
 document.getElementById('transactionTitle').textContent=kind==='deposit'?'Deposit Funds':'Withdraw Funds';
 document.getElementById('txMessage').textContent='';
 modal.classList.add('show');
}));
document.querySelectorAll('[data-amount]').forEach(btn=>btn.addEventListener('click',()=>document.getElementById('amount').value=btn.dataset.amount));
const txForm=document.getElementById('transactionForm');
const depositEntry=document.getElementById('depositEntry');
const depositInstructions=document.getElementById('depositInstructions');
const depositStatus=document.getElementById('depositStatus');

if(txForm)txForm.addEventListener('submit',async e=>{
 e.preventDefault();
 const kind=document.getElementById('transactionKind').value;
 const msg=document.getElementById('txMessage');
 if(kind==='deposit'){
  const amount=Number(document.getElementById('amount').value);
  if(!Number.isFinite(amount)||amount<1000){msg.textContent='Enter at least UGX 1,000.';return;}
  document.getElementById('depositDisplayAmount').textContent='UGX '+amount.toLocaleString('en-US');
  depositEntry.classList.add('hidden');
  depositInstructions.classList.remove('hidden');
  depositStatus.textContent='';
  return;
 }
 try{
  const res=await fetch('/transaction',{method:'POST',body:new FormData(txForm)});
  const data=await res.json();
  msg.textContent=data.message;
  msg.style.color=data.ok?'#078e89':'#b42318';
 }catch(err){msg.textContent='Could not save request. Please try again.';}
});

const copyPaymentNumber=document.getElementById('copyPaymentNumber');
if(copyPaymentNumber)copyPaymentNumber.addEventListener('click',async()=>{
 try{await navigator.clipboard.writeText('0758878297');copyPaymentNumber.textContent='Copied';}
 catch(err){copyPaymentNumber.textContent='Number: 0758878297';}
});

const depositBack=document.getElementById('depositBack');
if(depositBack)depositBack.addEventListener('click',()=>{
 depositInstructions.classList.add('hidden');
 depositEntry.classList.remove('hidden');
});

const depositSent=document.getElementById('depositSent');
if(depositSent)depositSent.addEventListener('click',async()=>{
 const amount=document.getElementById('amount').value;
 const channel=txForm.elements.channel.value;
 const reference=document.getElementById('depositReference').value.trim();
 const data=new FormData();
 data.append('kind','deposit');
 data.append('amount',amount);
 data.append('channel',channel);
 data.append('reference',reference);
 depositSent.disabled=true;
 depositStatus.textContent='Submitting your deposit for verification...';
 try{
  const res=await fetch('/transaction',{method:'POST',body:data});
  const result=await res.json();
  depositStatus.textContent=result.message;
  depositStatus.style.color=result.ok?'#087a37':'#b42318';
 }catch(err){depositStatus.textContent='Could not submit. Please try again.';depositStatus.style.color='#b42318';}
 finally{depositSent.disabled=false;}
});

const slides=[['Invest Smart<br>Live Healthy','with PIMCO Investment Platform. Grow your future with informed choices.'],['Health and Future','Explore medical equipment and learn about healthy living.'],['Together for Uganda','Building a healthier future starts with informed choices.']];
let slide=0;setInterval(()=>{const h=document.getElementById('heroTitle');if(!h)return;slide=(slide+1)%slides.length;h.innerHTML=slides[slide][0];},4200);
