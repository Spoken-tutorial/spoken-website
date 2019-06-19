import { Component, OnInit } from '@angular/core';
import { FossService } from '../_service/foss.service';
import { TutorialsService } from '../_service/tutorials.service'

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass']
})
export class HomeComponent implements OnInit {

  public foss;
  public tutorials;
  public fid;

  constructor(
    public fossService: FossService,
    public tutorialService: TutorialsService
  ) { }

  LanguageSelected(language) {
    // console.log(language);
  }

  public fetchFossTutorials(fid) {
    this.tutorialService.getFossTutorials(fid).subscribe(
      (res) => {
        this.tutorials = res
      },
      (err) => {
        console.log('Failed to fetch tutorial categories');
        console.error(err);
      }
    );
  }

  fetchAllFoss() {
    this.fossService.getAllFossCategories().subscribe(
      (res) => this.foss = res,
      (err) => {
        console.log('Failed to fetch foss categories');
        console.error(err);
      }
    );
  }

  ngAfterViewInit() {
    this.fetchAllFoss();
  };

  ngOnInit() {
  };

}
